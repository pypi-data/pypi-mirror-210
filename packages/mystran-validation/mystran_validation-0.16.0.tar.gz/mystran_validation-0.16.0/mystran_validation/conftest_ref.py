# content of conftest.pybreakpoint()
import ast
import configparser
import numbers
import os
import shlex
import shutil
import subprocess
import traceback
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from femap_neutral_parser import Parser as NeuParser

from mystran_validation import assert_frame_equal, cleandir, diffxlsx_target
from mystran_validation.parsers import subset
from mystran_validation.parsers.nastran_op2 import Parser as OP2Parser
from mystran_validation.utils import booleanify

# =============================================================================
# test collection
# =============================================================================


def pytest_collection_modifyitems(items):
    """add CARDs to marks"""
    for item in items:
        bulk_file = item.spec["bulk"]
        with open(bulk_file, "r") as fh:
            lines = fh.readlines()
        words = set(
            [
                line.split(" ")[0].strip()
                for line in lines
                if not line.startswith("$")
                and not line.startswith("+")
                and not line.startswith("PARAM,")
                and not line.startswith("CORD,")
            ]
        ) - set(
            [
                "",
                " ",
                "PARAM",
                "CEND",
                "ENDDATA",
                "NASTRAN",
                "ID",
                "GRID",
                "SUBCASE",
                "TIME",
                "BEGIN",
                "SOL",
                "INIT",
            ]
        )
        for tag in words:
            item.add_marker(getattr(pytest.mark, tag))
        # ---------------------------------------------------------------------
        # user-defined marks
        marks = item.spec.get("marks", ())
        if marks:
            marks = [m.strip() for m in marks.split(",")]
            for mark in marks:
                item.add_marker(getattr(pytest.mark, mark))


def pytest_collect_file(parent, path):
    _path = Path(path)
    if _path.suffix == ".ini" and _path.name.startswith("test"):
        return IniTestFile.from_parent(parent, fspath=path)


class IniTestFile(pytest.File):
    bulkfile = None
    rootdir = None
    rootname = None
    mystran_run_status = {}
    reference = {}
    op2s = {}

    def collect(self):
        config = configparser.ConfigParser()
        config.read(self.fspath)
        # ---------------------------------------------------------------------
        # prepare paths
        self.rootdir = Path(self.fspath).parent
        self.rootname = Path(self.fspath).stem
        # ---------------------------------------------------------------------
        # clean working dir
        wdir = self.rootdir / (".out_" + self.rootname)
        for name in config.sections():
            if name.startswith("_"):
                continue
            spec = dict(config[name].items())
            spec["test-config"] = Path(self.fspath)
            # =================================================================
            # building and yielding atomic test [name]
            # =================================================================
            bulkfile = self.rootdir / spec["bulk"]
            if self.bulkfile:
                if bulkfile != self.bulkfile:
                    raise ValueError(f"{name}: One class, one bulk, one output!")
            else:
                self.bulkfile = bulkfile
            spec["workingdir"] = wdir
            spec["internal_link"] = str(
                Path(self.fspath).relative_to(self.rootdir.parent)
            )
            spec["bulk"] = bulkfile
            ref = spec["reference"]
            # -----------------------------------------------------------------
            # if ref is obviously a file
            if Path(ref).suffix.lower() in (".op2", ".neu"):
                spec["reference"] = self.rootdir / spec["reference"]
            # -----------------------------------------------------------------
            # if ref a sing value
            else:
                ref = float(ref)
                spec["reference"] = ref
            spec["rtol"] = float(spec.get("rtol", 1e-05))
            spec["atol"] = float(spec.get("atol", 1e-08))
            spec["shortdesc"] = spec.get("shortdesc", "")
            spec["output"] = spec["workingdir"] / (bulkfile.stem + ".NEU")
            spec["output_f06"] = spec["workingdir"] / (bulkfile.stem + ".F06")
            spec["diffxlsx"] = spec["workingdir"] / (bulkfile.stem + ".NEU")
            yield IniItem.from_parent(self, name=name, spec=spec)


class IniItem(pytest.Item):
    """Atomic test. This is where one single [test] is performed"""

    def __init__(self, name, parent, spec):
        super().__init__(name, parent)
        self.spec = spec

    def run_mystran(self):
        """run bulkfile"""
        wdir = self.spec["workingdir"]
        cleandir(wdir)
        target = shutil.copy(self.spec["bulk"], self.spec["workingdir"])
        cmd = f"{os.getenv('MYSTRAN_BIN')} {target}"
        status = subprocess.check_output(
            shlex.split(cmd),
            stderr=subprocess.STDOUT,
        )
        if "fatal" in status.decode().lower():
            # retrieve Error
            target = Path(target)
            error_file = target.parent / (target.stem + ".ERR")
            # f06_file = target.parent / (target.stem + ".F06")
            with open(error_file, "r") as fh:
                lines = fh.readlines()
            errors = []
            _parsing_error = False
            for line in lines:
                line = line.strip()
                if _parsing_error:
                    if line.startswith("*"):
                        errors.append(tuple(_parsing_error))
                        _parsing_error = False
                    else:
                        _parsing_error.append(line)
                if line.startswith("*ERROR"):
                    _parsing_error = [line]
            if _parsing_error:
                errors.append(tuple(_parsing_error))
            errors = ["\n".join(err) for err in errors]
            raise MystranException(errors[0])
        # ---------------------------------------------------------------------
        # get actual results
        neu = NeuParser(self.spec["output"])
        self.parent.actual = neu
        self.parent.actual.info(doprint=False)  # pre-digest data
        self.parent.actual_available_vectors = sorted(
            self.parent.actual._output_vectors.keys()
        )
        return status

    def expected(self, vector, filters=None, axis=None, raw=False):
        """build reference (expected) DataFrame"""
        if not filters:
            filters = {}
        df_expected = None
        # ---------------------------------------------------------------------
        # reference is a numerical value
        if isinstance(self.spec["reference"], numbers.Number):
            if axis is None:
                raise ValueError("param `axis` must be specified for manual checking")
            _data = filters.copy()
            _data.update({axis: [self.spec["reference"]]})
            df_expected = pd.DataFrame(_data)
            df_expected.set_index(list(filters.keys()), inplace=True)
            df_expected = df_expected[axis].to_frame()
        # ---------------------------------------------------------------------
        # reference is a ref file
        elif self.spec["reference"].suffix.lower() == ".op2":
            op2 = self.parent.op2s[self.spec["reference"]]
            df_expected = op2.get(vector=vector, raw=raw, **filters)
        else:
            raise ValueError("reference {self.spec['reference']} not understood")
        return df_expected

    def actual(self, vector, filters=None, axis=None):
        """build actual DataFrame"""
        if not filters:
            filters = {}
        # ---------------------------------------------------------------------
        # as of femap_neutral_parser 0.8, vectos have been renamed
        compat = {
            "reactions": "spc_forces",
        }
        if vector in compat:
            warnings.warn(
                f"``{vector}`` is deprecated. Use ``{compat[vector]}`` instead"
            )
        vector = compat.get(vector, vector)
        # -----------------------------------------------------------------
        # get values from neutral file, and reshape it
        df_actual = self.parent.actual.get(vector, asdf=True)
        df_actual = subset(df_actual, **filters)
        if axis:
            try:
                df_actual = df_actual[axis].to_frame()
            except KeyError:
                msg = f"{axis} is not a proper column. Use one of {df_actual.columns.tolist()}"
                raise KeyError(msg)
        return df_actual

    def runtest(self):
        """trigger pytest"""
        self.user_properties += [("bulk", str(self.spec["bulk"]))]
        self.user_properties += [("ref", str(self.spec["reference"]))]
        self.user_properties += [("description", self.spec["description"])]
        self.user_properties += [("atol", self.spec["atol"])]
        self.user_properties += [("rtol", self.spec["rtol"])]
        self.user_properties += [("shortdesc", self.spec["shortdesc"])]
        self.user_properties += [("vector", self.spec["vector"])]
        self.user_properties += [("marks", set([m.name for m in self.own_markers]))]
        self.user_properties += [("test-config", self.spec["test-config"])]
        self.user_properties += [("internal_link", self.spec["internal_link"])]
        self.user_properties += [
            ("workingdir", str(Path(self.spec["workingdir"]).parent.parent))
        ]
        self.user_properties += [
            ("confidential", booleanify(self.spec.get("confidential", False)))
        ]
        if self.spec.get("skip"):
            pytest.skip(self.spec["skip"])
        # ---------------------------------------------------------------------
        # run Mystran only once
        if self.spec["bulk"] not in self.parent.mystran_run_status:
            # first test for this class, a few things to set up
            retmystran = self.run_mystran()
            self.parent.mystran_run_status[self.spec["bulk"]] = retmystran
        # process OP2 only once
        ref = self.spec["reference"]
        if not isinstance(ref, numbers.Number):
            if ref.suffix.lower() == ".op2" and str(ref) not in self.parent.op2s:
                self.parent.op2s[ref] = OP2Parser(str(self.spec["reference"]))
            self.op2 = self.parent.op2s[ref]  # shortcut for self
        else:
            self.op2 = None
        self.user_properties += [("output", str(self.spec["output"]))]
        self.user_properties += [("output_f06", str(self.spec["output_f06"]))]
        try:
            vector = self.spec["vector"]
            # ---------------------------------------------------------------------
            # get subset index
            filters = dict(
                SubcaseID=ast.literal_eval(self.spec.get("subcaseids", "None")),
                NodeID=ast.literal_eval(self.spec.get("nodeids", "None")),
                ElementID=ast.literal_eval(self.spec.get("elementids", "None")),
            )
            axis = self.spec.get("axis")
            filters = {k: [v] for k, v in filters.items() if v}
            # ---------------------------------------------------------------------
            # get dataframes to compare
            df_actual = self.actual(vector, filters, axis)
            df_expected = self.expected(vector, filters, axis)
            # -----------------------------------------------------------------
            # check tolerances
            rtol = self.spec["rtol"]
            atol = self.spec["atol"]
            failing, failures, aerr, rerr = assert_frame_equal(
                df_actual, df_expected, rtol=rtol, atol=atol
            )
        except Exception as exc:
            tb = traceback.format_exc()
            raise GenericException(self, exc, tb)
        else:
            if len(failures) > 0:
                # dump comparisons performed
                if len(failures) > 0:
                    xlsxdiff_target = diffxlsx_target(self.parent.name)
                    xlsx_filepath = dump(
                        df_expected,
                        df_actual,
                        target=xlsxdiff_target,
                        sheetname=self.name,
                        failing=failing,
                    )
                    self.user_properties += [("xlsxdiff", xlsxdiff_target)]
                raise IniException(
                    self, df_actual, df_expected, failures, rtol, atol, aerr, rerr
                )

    def repr_failure(self, excinfo):
        """Called when self.runtest() raises an exception."""
        if isinstance(excinfo.value, MystranException):
            return excinfo.value
        elif isinstance(excinfo.value, IniException):
            (
                item,
                df_actual,
                df_expected,
                failures,
                rtol,
                atol,
                aerr,
                rerr,
            ) = excinfo.value.args
            df_actual = df_actual.loc[failures.index]
            df_expected = df_expected.loc[failures.index]
            # failing difference
            return "\n".join(
                [
                    f"usecase `{self.fspath}::[{self.name}]`\nexecution failed given precision requirements:\n  * {atol=}\n  * {rtol=}\n",
                    f"failing with:\n  * Absolute difference {aerr=}\n  * Relative difference {rerr=}\n",
                    f"Expected\n--------\n{df_expected}\n",
                    f"Actual\n------\n{df_actual}",
                ]
            )
        elif isinstance(excinfo.value, GenericException):
            item, exc, traceback = excinfo.value.args
            return "\n".join(
                [
                    f"usecase `{self.fspath}::[{self.name}]` raised the following exception\n",
                    f"{exc}\n",
                    f"file: {traceback}",  # get rid of "file " prefix
                ]
            )

    def reportinfo(self):
        return self.fspath, 0, f"usecase: {self.name}"


class IniException(Exception):
    pass


class MystranException(Exception):
    pass


class GenericException(Exception):
    pass


def apply_color(x, failing):
    # colors = {False: "green", True: "red; font-weight: bold", "ref": "black"}
    colors = {
        False: "green",
        True: "red; text-decoration: line-through;",
        "ref": "black",
    }
    return failing.applymap(lambda val: "color: {}".format(colors.get(val, "")))


def highlight_columns(x):
    if x.name[1] == "mystran":
        style = "background-color: azure"
    else:
        style = "background-color: white"
    return [style] * x.shape[0]


def dump(df_expected, df_actual, target, sheetname, failing, debug=False):
    full = pd.concat({"ref.": df_expected, "mystran": df_actual}).unstack(level=0)
    # reshape failing to have same format as `full`
    _ref = pd.DataFrame(
        data=np.full_like(failing, "ref", dtype=object),
        index=failing.index,
        columns=failing.columns,
    )
    _failing = pd.concat({"ref.": _ref, "mystran": failing}).unstack(level=0)
    # ensure columns are ordered as `full` DF
    _failing = _failing[[c for c in full.columns]]
    # =========================================================================
    # formatting
    # =========================================================================
    mode = "a" if target.exists() else "w"
    # style dataframe
    styled = full.style.apply(apply_color, axis=None, failing=_failing)
    styled = styled.apply(highlight_columns)
    with pd.ExcelWriter(target, mode=mode, engine="openpyxl") as writer:
        styled.to_excel(writer, sheet_name=sheetname)
    return target
