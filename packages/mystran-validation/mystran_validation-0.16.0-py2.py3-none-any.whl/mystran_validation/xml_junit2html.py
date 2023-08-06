import configparser
import datetime as dt
import glob
import logging
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import pandas as pd
import pkg_resources
from jinja2 import Environment, FileSystemLoader, PackageLoader

from mystran_validation import acopy, cleandir, get_conf
from mystran_validation.utils import getext, relpath, slugify, working_directory

try:
    loader = PackageLoader("mystran_validation", "data/html_template.j2")
except ValueError:
    logging.info("`mystran-validation is probably installed via `pip install -e .`")
    logging.info("logging from FileSystem")
    tpl_folder = (pkg_resources.resource_filename("mystran_validation", "data"),)
    logging.info(f"{tpl_folder=}")
    loader = FileSystemLoader(tpl_folder)
env = Environment(loader=loader)
env.filters["slugify"] = slugify
env.filters["getext"] = getext
env.filters["relpath"] = relpath


class TestSuite:
    """TestSuite: container for all testsuite test cases. Normally, this is only one."""

    def __init__(self, xml):
        self.meta = xml.attrib
        self.testcases = {}
        # ---------------------------------------------------------------------
        # configure XML / HTML / assets dir
        config_fpath, config = get_conf()
        for i, tc in enumerate(xml.findall("./testcase")):
            tcobject = TestCase(tc)
            if tcobject.classname not in self.testcases:
                tcparent = TestCaseParent(tcobject.classname)
                self.testcases[tcobject.classname] = tcparent
            self.testcases[tcobject.classname].add_test_case(tcobject)

    def __repr__(self):
        return "testsuite errors={errors} failures={failures} skipped={skipped} tests={tests} time={time} timestamp={timestamp}".format(
            **self.meta
        )


class TestCaseParent:
    """thin wrapper equivalent to ini file"""

    def __init__(self, classname):
        self.classname = classname
        self.testcases = []
        self.meta = {}
        self._status = defaultdict(int)
        self.marks = set()
        self.assets = defaultdict(dict)
        self.rel_assets = defaultdict(dict)
        self.test_config = configparser.ConfigParser()
        self.rootdir = None

    def get_assets(self, tcobject, section):
        cfg = dict(self.test_config[section].items())
        if self.rootdir is None:
            self.rootdir = Path(tcobject.properties["test-config"]).parent
        if section == "DEFAULT":
            neutral_output = tcobject.properties.get("output")
            if neutral_output:
                cfg["neutral output"] = neutral_output
            f06_output = tcobject.properties.get("output_f06")
            if f06_output:
                cfg["F06 output"] = f06_output
            femap_dir = self.rootdir / "Femap"
            # collect special Femap folder assets
            if femap_dir.exists():
                f06 = femap_dir.glob(Path(self.short_classname).stem + ".f06")
                try:
                    cfg["NX F06 output"] = list(f06)[0]  # only one expected
                except IndexError:
                    pass  # no f06 found
            # also collect user defined assets
            if "__ASSETS__" in self.test_config.sections():
                assets_cfg = dict(self.test_config["__ASSETS__"].items())
                for k, v in assets_cfg.items():
                    if cfg.get(k) == v:
                        # already in config. Continue
                        continue
                    if (",") in v:
                        path, key = [t.strip() for t in v.split(",")]
                    else:
                        path = v
                        key = " ".join([token.title() for token in k.split("_")])
                    path = self.rootdir / Path(path)
                    if path.exists():
                        self.assets[section][key] = self.rootdir / Path(path)
        else:
            # get only keys differing from "DEFAULT"
            default_cfg = dict(self.test_config[section].items())
            cfg = {k: v for k, v in cfg.items() if v != default_cfg.get(k)}
            xlsxdiff = tcobject.properties.get("xlsxdiff")
            if xlsxdiff and Path(xlsxdiff).exists():
                self.assets[section]["xlsxdiff"] = Path(xlsxdiff)
        for k in ("bulk", "reference", "neutral output", "F06 output", "NX F06 output"):
            if k in cfg:
                path = self.rootdir / Path(cfg[k])
                if path.exists():
                    self.assets[section][k] = path
        if section == "DEFAULT":
            # also check for figure file: <bulkname>.png
            bulkfile = self.assets["DEFAULT"]["bulk"]
            optional_figfile = bulkfile.parent / (bulkfile.stem + ".png")
            if optional_figfile.exists():
                self.assets["DEFAULT"]["fig"] = optional_figfile

    def copy_assets(self, section):
        """copy files and store assets as path relative to HTML file"""
        html_outdir = Path(os.environ["MYSTRAN_VALIDATION_BUILDDIR"])
        assets_outdir = html_outdir / "assets" / Path(self.classname).stem / section
        cleandir(assets_outdir, parents=True)
        assets = dict(self.assets).get(section, {})
        if "xlsxdiff" in assets:
            if "xlsxdiff" not in self.rel_assets["DEFAULT"]:
                target = assets_outdir.parent / "DEFAULT" / assets["xlsxdiff"].name
                acopy(assets["xlsxdiff"], target)
                self.rel_assets["DEFAULT"]["xlsxdiff"] = target.relative_to(html_outdir)
            assets.pop("xlsxdiff")
        for k, src in assets.items():
            # if k == "xlsxdiff":
            #     breakpoint()
            target = assets_outdir / src.name
            acopy(src, target)
            target = target.relative_to(html_outdir)
            self.rel_assets[section][k] = target

    def __hash__(self):
        return hash(self.classname)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.classname == other.classname

    def add_test_case(self, tcobject):
        if not self.testcases:
            # actions to perform once only
            try:
                tcprops = tcobject.properties["test-config"]
            except KeyError:
                logging.warning(f"no `test-config` properties for {tcobject=}")
                return
            self.test_config.read(tcprops)
            self.get_assets(tcobject, section="DEFAULT")
            self.shortdesc = tcobject.properties.pop("shortdesc", "")
            self.copy_assets("DEFAULT")
        self.get_assets(tcobject, section=tcobject.name)
        self.copy_assets(section=tcobject.name)
        self.testcases.append(tcobject)
        self._status[tcobject.status] += 1
        self.marks |= eval(tcobject.properties.get("marks", "set()"))

    @property
    def short_classname(self):
        return "/".join(self.classname.split(".")[1:-1]) + ".ini"

    @property
    def html_status(self):
        msg = []
        for status, nb in self._status.items():
            msg.append(f'<span class="alert-{status}">{status}</span>')
        return " ".join(msg)


class TestCase:
    def __init__(self, xml):
        # here we already have {"classname": "path.to.local.file", ...}
        for k, v in xml.attrib.items():
            setattr(self, k, v)
        self.properties = {}
        for prop in xml.findall("./properties/property"):
            self.properties[prop.attrib["name"]] = prop.attrib["value"]
        # ---------------------------------------------------------------
        # skipped
        skipped = xml.find("./skipped")
        if skipped is not None:
            self.skipped = skipped.attrib
        else:
            self.skipped = None
        # ---------------------------------------------------------------
        # failed
        failure = xml.find("./failure")
        if failure is not None:
            self.failure = failure.attrib
        else:
            self.failure = None

    def __repr__(self):
        try:
            short_classname = str(
                Path(self.properties["test-config"]).relative_to(
                    Path(self.properties["workingdir"])
                )
            )
        except KeyError:
            short_classname = f"{self.name} parent"
        return f"{short_classname}::{self.name}"

    @property
    def status(self):
        if self.skipped:
            return "skipped"
        elif self.failure:
            return "failed"
        return "success"


def parse_xml(filepath):
    """parse JUnit  XML file and return a tuple of `TestSuite` instances"""
    fpath = Path(filepath)
    assert fpath.exists()
    tree = ET.parse(filepath)
    root = tree.getroot()
    # get all testsuites
    ret = []
    for ts in root.findall("./testsuite"):
        ret.append(TestSuite(ts))
    return tuple(ret)


def xml2html(xmlfpath, make_matrix=True):
    # get mystranversion
    version, date = os.environ["MYSTRAN_VALIDATION_VERSION"].split("___")
    # =========================================================================
    # generate run HTML output
    # =========================================================================
    tss = parse_xml(xmlfpath)
    rtemplate = env.get_template("html_template.j2")
    kwargs = {
        "rootdir": os.environ["MYSTRAN_VALIDATION_ROOTDIR"],
        "mystran_version": version,
        "mystran_date": date,
    }
    kwargs["testsuites"] = tss
    kwargs["publication_date"] = dt.datetime.now()
    # return rtemplate.render(kwargs)
    # =========================================================================
    # generate matrix / index
    # =========================================================================
    itemplate = env.get_template("html_index.j2")
    rootdir = Path(os.environ["MYSTRAN_VALIDATION_ALLBUILDS"])

    with working_directory(rootdir):
        xmls = glob.glob("**/mystran-testing.xml", recursive=True)
    xmls = {os.path.split(xml)[0]: parse_xml(rootdir / xml)[0] for xml in xmls}
    matrix = defaultdict(dict)
    for version, ts in xmls.items():
        for ini_name, tcparent in ts.testcases.items():
            for tc in tcparent.testcases:
                matrix[version][
                    tc.__repr__().replace("mystran-test-cases.", "")
                ] = tc.status
    matrix = pd.DataFrame(dict(matrix))
    matrix.columns = [c.replace("___", " (") + ")" for c in matrix.columns]
    index = itemplate.render({"runs": list(xmls.keys()), "matrix": matrix})
    return index, rtemplate.render(kwargs)
