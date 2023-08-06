# -*- coding: utf-8 -*-

"""Top-level package for MYSTRAN validation."""

__author__ = """Nicolas Cordier"""
__email__ = "nicolas.cordier@numeric-gmbh.ch"
__version__ = "0.16.0"

import asyncio
import configparser
import datetime as dt
import logging
import os
import shutil
from functools import wraps
from pathlib import Path

import click
from appdirs import AppDirs

from .utils import slugify


def assert_frame_equal(dfa, dfb, atol, rtol):
    """it's hard to understand how pandas tesing is actually working
    better to fall back to numpy testing, assuming we do not need to
    check columns, index, etc...
    """
    # reorder columns
    dfb = dfb[[c for c in dfa if c in dfb]]
    diff = abs(dfa - dfb)
    crit = atol + rtol * abs(dfb)
    failing = diff[diff > crit]
    # keep rows and columns where at least one failure occurs
    failures = failing.dropna(how="all").dropna(how="all", axis=1)
    abs_error = failing.max().max()
    rel_error = (failing / abs(dfb)).max().max()
    failing = diff > crit
    return failing, failures, abs_error, rel_error


def background(func):
    """decorator for background jobs"""

    @wraps(func)
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, func, *args, *kwargs)

    return wrapped


@background
def acopy(src, dest, **kwargs):
    logging.debug(f"{src}->{dest}")
    shutil.copy(src, dest, **kwargs)


def cleandir(target, **kwargs):
    if not isinstance(target, Path):
        target = Path(target)
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(**kwargs)


def diffxlsx_target(name):
    dumping_dir = Path(os.environ["MYSTRAN_VALIDATION_BUILDDIR"]) / "dumps"
    dumping_dir.mkdir(exist_ok=True, parents=True)
    target = dumping_dir / (slugify(str(name)) + ".xlsx")
    return target


# =============================================================================
# CONFIGURATION stuff and default options
# =============================================================================
DIRS = AppDirs("mystran-validation", "numeric")

DEFAULTS = {
    "DEFAULT": {
        "mystran-bin": os.getenv("MYSTRAN_BIN", shutil.which("mystran")),
        "rootdir": os.path.join(DIRS.user_data_dir, "mystran-test-cases"),
        "report": True,
        "open-report": True,
        "builddir": "_build",
        "rsync": "",
    }
}

DEFAULTS_HELP = {
    "mystran-bin": {
        "help": "path to mystran binary",
        "type": click.Path(
            exists=True,
            file_okay=True,
            dir_okay=False,
            executable=True,
            resolve_path=True,
            path_type=None,
        ),
    },
    "rootdir": {
        "help": "test-cases repository",
        "type": click.Path(
            exists=False,
            file_okay=False,
            dir_okay=True,
            executable=True,
            resolve_path=True,
            path_type=None,
        ),
        "create": True,
    },
    "report": {"help": "create reporting", "type": bool, "coerce": (int, str)},
    "open-report": {
        "help": "open generated report",
        "type": bool,
        "coerce": (int, str),
    },
    "builddir": {"help": "build directory"},
    "rsync": {"help": "rsync command for publishing"},
}


def _create_profile(profile_name, interactive=False, **kwargs):
    """create a non-existing profile, assuming config file exists"""
    if profile_name == "DEFAULT":
        interactive = True
    parser = configparser.ConfigParser()
    params = DEFAULTS.copy()
    # -------------------------------------------------------------------------
    # copy DEFAULT
    if profile_name not in params:
        params[profile_name] = {}
    for k, v in kwargs.items():
        if not v:
            continue
        params[profile_name][k.replace("_", "-")] = v
    # -------------------------------------------------------------------------
    # confirm values to be created
    for k, v in params[profile_name].items():
        helper = DEFAULTS_HELP.get(k, {})
        msg = helper["help"]
        default = v
        typ = helper.get("type", type(v))
        coerce = helper.get("coerce", tuple())
        create_it = helper.get("create", False)
        if interactive:
            newv = click.prompt(f"{msg}?", default=default, type=typ)
        else:
            newv = default
        if create_it:
            path = Path(newv).expanduser()
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                # TODO: expand example test case
        if coerce:
            for func in coerce:
                newv = func(newv)
        parser[profile_name][k] = newv
    config_fpath = Path(DIRS.user_config_dir) / "config.ini"
    with open(config_fpath, "w") as configfile:
        parser.write(configfile)


def init_config(profile_name="DEFAULT", **kwargs):
    """create/update a profile in the config file. If config file not found,
    create it from scratch
    """
    config_fpath = Path(DIRS.user_config_dir) / "config.ini"
    if not config_fpath.exists():
        config_fpath.parent.mkdir(parents=True, exist_ok=True)
        config_fpath.touch()
        logging.debug(f"created {config_fpath}")
        click.echo(
            click.style(f"created configuration file {config_fpath}", fg="green")
        )
        click.echo("consider to modify this file as per your preferences")
    # check if profile already exists
    parser = configparser.ConfigParser()
    parser.read(config_fpath)
    if dict(parser[profile_name].items()) == {}:
        _create_profile(profile_name, **kwargs)
        logging.debug(f"created {config_fpath}[{profile_name}]")
        click.echo(
            click.style(f"created configuration profile {profile_name}", fg="green")
        )
    return config_fpath


def is_comment(param):
    return param.strip()[0] in ("#", ";")


def get_conf():
    config_fpath = Path(DIRS.user_config_dir) / "config.ini"
    if not config_fpath.exists():
        config_fpath = init_config()
    parser = configparser.ConfigParser()
    parser.read(config_fpath)
    # -------------------------------------------------------------------------
    # always check if "DEFAULT" is up-to-date
    defaults = set((p for p in DEFAULTS["DEFAULT"].keys() if not is_comment(p)))
    actual = set((p for p in parser["DEFAULT"].keys() if not is_comment(p)))
    if defaults ^ actual:
        # some changes will occur, backup initial config
        backup_fpath = config_fpath.parent / (
            config_fpath.stem
            + ".ini.backup_"
            + dt.datetime.now().isoformat(timespec="minutes")
        )
        with open(backup_fpath, "w") as configfile:
            parser.write(configfile)
        logging.info(f"backuped {backup_fpath} before modification")
    # missing parameters
    for missing_param in defaults - actual:
        parser["DEFAULT"][missing_param] = DEFAULTS["DEFAULT"][missing_param]
        logging.info(f"added missing parameter {missing_param}")
    # unknown parameters
    for unknown_param in actual - defaults:
        _val = parser["DEFAULT"].pop(unknown_param)
        logging.warning(f"removed unknown parameter {unknown_param}={_val}")
    with open(config_fpath, "w") as configfile:
        parser.write(configfile)
    return config_fpath, parser


def get_profile(config, profile_name=None):
    if profile_name:
        try:
            config = dict(config[profile_name].items())
        except KeyError:
            msg = f"{profile_name} not defined in configuration file"
            raise KeyError(msg)
    else:
        config = dict(config["DEFAULT"].items())
    for k, v in config.items():
        config[k] = os.path.expanduser(v)
    return config
