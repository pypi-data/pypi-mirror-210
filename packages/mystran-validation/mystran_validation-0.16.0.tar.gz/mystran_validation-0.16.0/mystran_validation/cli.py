# -*- coding: utf-8 -*-

"""Console script for mystran_validation.

MYSTRAN Binary is found with the following scheme:

    * from `--mystran-bin` passed option
    * from "MYSTRAN_BIN" environment variable
    * from /usr/bin/mystran
"""
import glob
import logging
import os
import shlex
import shutil
import subprocess as sp
import sys
import webbrowser
from pathlib import Path

import click
import pkg_resources
import pytest

from mystran_validation import __version__, cleandir, get_conf, get_profile, init_config
from mystran_validation.utils import get_mystran_version
from mystran_validation.xml_junit2html import xml2html


def find(
    path,
    extensions,
    name="*",
    break_on_first=True,
    return_first=True,
):
    """return a list of pathlib.Path canditates matching {name}{ext}"""
    if isinstance(path, str):
        path = Path(path)
    path = path  # .resolve()
    files = []
    for ext in extensions:
        pattern = str(path / f"{name}{ext}")
        _files = glob.glob(pattern)
        if _files:
            if break_on_first:
                files = _files
                break
            files += _files
    if not files:
        files = [None]
    else:
        files = [Path(f) for f in files]
    if return_first:
        return files[0]
    return files


def get_junit_files():
    junit_file = (
        Path(os.environ["MYSTRAN_VALIDATION_BUILDDIR"]) / f"mystran-testing.xml"
    )
    junit_html_target = junit_file.parent / "index.html"
    return junit_file, junit_html_target


def setup(clean=True):
    # -------------------------------------------------------------------------
    # ensure conftest.py and __init__ is there
    rootdir = Path(os.environ["MYSTRAN_VALIDATION_ROOTDIR"])
    _init = rootdir / "__init__.py"
    if not _init.exists():
        _init.touch()
    _conftest = rootdir / "conftest.py"
    if not _conftest.exists():
        with open(_conftest, "w") as fh:
            fh.write("from mystran_validation.conftest_ref import *\n")
    # =========================================================================
    # clean relevant output dir
    # =========================================================================
    if clean:
        cleandir(os.environ["MYSTRAN_VALIDATION_BUILDDIR"], parents=True)


def teardown(rootdir):
    """clean rootdir"""
    to_delete = ["**/bandit.*", "conftest.py", "__init__.py", "__pycache__"]
    to_delete = [rootdir / p for p in to_delete]
    for pattern in to_delete:
        files = glob.glob(str(pattern), recursive=True)
        logging.debug(f"deleting temporary files:")
        for file in files:
            logging.debug(f" * {file}")
            try:
                shutil.rmtree(file)
            except NotADirectoryError:
                os.remove(file)


def _init_rootdir(rootdir):
    path = rootdir / "example"
    click.echo(click.style(f"creating missing test-cases repository...", bold=True))
    click.echo(click.style(f"created repository {path}", fg="green"))
    path.mkdir(parents=True, exist_ok=True)
    # copy example files
    _files = ["bulk_model.nas", "bulk_model_2.dat", "test_bar.ini", "test_case_03.op2"]
    for f in _files:
        src = Path(pkg_resources.resource_filename("mystran_validation.data", f))
        shutil.copy(src, path / f)
    return path


def _ensure_paths(profile_name, rootdir, mystran_bin):
    # -------------------------------------------------------------------------
    # get configuration
    config_fpath, config = get_conf()
    # -------------------------------------------------------------------------
    # get profile
    get_profile(config, profile_name)


@click.group(invoke_without_command=True)
@click.option(
    "-p", "--profile", default="DEFAULT", type=str, help="configuration title"
)
@click.option("-r", "--rootdir")
@click.option("-m", "--mystran-bin")
@click.option("-l", "--loglevel", default="info", type=str)
@click.pass_context
def main(ctx, profile, rootdir, mystran_bin, loglevel):
    # profile_name = profile  # profile will be used for dict
    # -------------------------------------------------------------------------
    # handling logging verbosity
    getattr(logging, loglevel.upper())
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % loglevel)
    logging.basicConfig(level=numeric_level)
    # =========================================================================
    # config and profile
    # =========================================================================
    config_fpath, config = get_conf()
    try:
        profile_obj = get_profile(config, profile)
    except KeyError:
        click.echo(
            click.style(
                f"no profile named `{profile}`. Consider amending {config_fpath}", "red"
            )
        )
        sys.exit(1)
    # =========================================================================
    # create environment variables
    # =========================================================================
    os.environ["MYSTRAN_VALIDATION_PROFILE"] = profile
    os.environ["MYSTRAN_BIN"] = profile_obj["mystran-bin"]
    os.environ["MYSTRAN_VALIDATION_ROOTDIR"] = profile_obj["rootdir"]
    os.environ["MYSTRAN_VALIDATION_VERSION"] = "{version}___{date}".format(
        **get_mystran_version()
    )
    os.environ["MYSTRAN_VALIDATION_BUILDDIR"] = os.path.join(
        profile_obj["rootdir"],
        profile_obj["builddir"],
        os.environ["MYSTRAN_VALIDATION_VERSION"],
    )
    os.environ["MYSTRAN_VALIDATION_ALLBUILDS"] = os.path.join(
        profile_obj["rootdir"],
        profile_obj["builddir"],
    )
    # =========================================================================
    # feed ctx.obj
    # =========================================================================
    ctx.ensure_object(dict)
    ctx.obj["rootdir"] = rootdir
    ctx.obj["mystran_bin"] = mystran_bin
    ctx.obj["profile"] = profile_obj
    if ctx.invoked_subcommand is None:
        click.echo(click.style(f"mystran-validation v{__version__}", "blue"))
        click.echo("run `mystran-val --help` for available options and commands")


@main.command()
@click.pass_context
def init(ctx):
    """ensure all required paths exist"""
    _ensure_paths(
        profile_name=os.environ["MYSTRAN_VALIDATION_PROFILE"],
        rootdir=os.environ["MYSTRAN_VALIDATION_ROOTDIR"],
        mystran_bin=os.environ["MYSTRAN_BIN"],
    )


# =============================================================================
# run
# =============================================================================
@main.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.option("--report/--no-report", default=None)
@click.option("--open-report/--not-open-report", default=None)
@click.option("--publish/--no-publish", default=False)
@click.option("--dump", type=click.IntRange(0, 3))
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx, report, open_report, dump, publish, pytest_args):
    """collect and run test-cases suite"""
    try:
        config_fpath, config = get_conf()
    except FileNotFoundError:
        click.echo(click.style("Configuration file not found!", "red"))
        click.echo(click.style("consider running `mystran-val init` first"))
        sys.exit(1)
    if report is None:
        report = bool(int(ctx.obj["profile"]["report"]))
    if open_report is None:
        open_report = bool(int(ctx.obj["profile"]["open-report"]))
    # -------------------------------------------------------------------------
    # check that mystran binary exists
    mystran_bin = Path(os.environ["MYSTRAN_BIN"])
    if not mystran_bin.exists():
        click.echo(click.style(f"Mystran Binary `{mystran_bin}` not found!", "red"))
        sys.exit(1)
    rootdir = Path(os.environ["MYSTRAN_VALIDATION_ROOTDIR"])
    if not rootdir.exists():
        click.echo(click.style(f"Rootdir `{rootdir}` not found!", "red"))
        sys.exit(1)
    # -------------------------------------------------------------------------
    # =========================================================================
    # summary
    # =========================================================================
    click.echo(click.style("test-cases params:", fg="green"))
    click.echo(
        click.style(
            (
                f"  * User global configuration={config_fpath}\n"
                "  * Mystran binary={MYSTRAN_BIN}\n"
                "  * root dir={MYSTRAN_VALIDATION_ROOTDIR}\n"
                "  * build dir={MYSTRAN_VALIDATION_BUILDDIR}\n"
            ).format(**os.environ),
            fg="green",
        )
    )
    bintxt = " ".join(os.environ["MYSTRAN_VALIDATION_VERSION"].split("___"))
    click.echo(
        click.style(
            "running MYSTRAN {}".format(bintxt),
            fg="green",
        )
    )
    click.echo("\n")
    # -------------------------------------------------------------------------
    # setting up rootdir
    pytest_args = list(pytest_args)
    if report:
        junit_file, junit_html_target = get_junit_files()
        pytest_args += [f"--junitxml={junit_file}"]
    pytest_args += ["--disable-pytest-warnings"]  # disable UnknownMarkWarning
    pytest_args.append(str(rootdir))
    setup()
    # =========================================================================
    # main pytest run command
    # =========================================================================
    pytest.main(pytest_args)
    if report:
        index_fpath = _make()
    teardown(rootdir)
    if report and open_report:
        webbrowser.open(str(index_fpath.resolve()))
    if publish:
        rsync_target = ctx.obj["profile"]["rsync"]
        if rsync_target:
            # rsync -av --exclude="mystran-testing.xml" _build/* numeric@AD:~/mv2/
            src = str(index_fpath.parent)
            rsync_bin = shutil.which("rsync")
            target = f'{rsync_target}{os.environ["MYSTRAN_VALIDATION_VERSION"]}/'
            click.echo(
                click.style(f"uploading {src} to {target}", bold=True, fg="green")
            )
            cmd = f'{rsync_bin} -av --exclude="mystran-testing.xml" {src}/ {target}/'
            cmdargs = shlex.split(cmd)
            # tree -H '.' -L 1 --noreport --charset utf-8 -P "*.zip" -o index.html
            sp.run(cmdargs, stdout=sp.DEVNULL)
    return 0


@main.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.argument("pytest_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def collect(ctx, pytest_args):
    """collect tests without running them (debugging purpises)"""
    try:
        config_fpath, config = get_conf()
    except FileNotFoundError:
        click.echo(click.style("Configuration file not found!", "red"))
        click.echo(click.style("consider running `mystran-val init` first"))
        sys.exit(1)
    profile = get_profile(config, os.environ["MYSTRAN_VALIDATION_PROFILE"])
    rootdir = Path(ctx.obj["rootdir"] if ctx.obj["rootdir"] else profile["rootdir"])
    setup(clean=False)
    args = list(pytest_args) + ["--collect-only"]
    args.append(str(rootdir))
    args += ["--disable-pytest-warnings"]  # disable UnknownMarkWarning
    pytest.main(args)
    teardown(rootdir)
    return 0


@main.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.pass_context
def make(ctx):
    index_fpath = _make()
    webbrowser.open(str(index_fpath.resolve()))
    return 0


def _make():
    junit_file, junit_html_target = get_junit_files()
    index, html = xml2html(junit_file, make_matrix=True)
    # index_fpath = junit_html_target.parent.parent / "index.html"
    # with open(index_fpath, "w") as fh:
    #     fh.write(index)
    with open(junit_html_target, "w") as fh:
        fh.write(html)
    return junit_html_target


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
