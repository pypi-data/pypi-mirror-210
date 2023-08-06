#! /usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import argparse as ap
import os
import shutil
import subprocess as sp
import enum
import sys


AnyPath = str | bytes | os.PathLike[str] | os.PathLike[bytes]


def user_home() -> str:
    if os.name == "nt":
        return os.environ["HOMEDRIVE"] + os.environ["HOMEPATH"]
    else:
        return os.environ["HOME"]


def resolve_env_crate_path() -> Path:
    if (path := os.environ.get("SSRS_CRATE_HOME", None)) is not None:
        return Path(path)
    if (data_home := os.environ.get("XDG_DATA_HOME", None)) is not None:
        return Path(data_home) / "ssrs"
    return Path(user_home()) / ".local" / "share" / "ssrs"


_env_crate_path: None | Path = None
def get_env_crate_path() -> Path:
    global _env_crate_path
    if _env_crate_path is None:
        _env_crate_path = resolve_env_crate_path()
        _env_crate_path.mkdir(exist_ok=True, parents=True)
    return _env_crate_path


def try_init_crate(dir_path: AnyPath) -> bool: # type: ignore
    proc = sp.run(["cargo", "init", "--bin", "."], cwd=dir_path, capture_output=True)
    match proc.returncode:
        case 101: return False            # noqa: True
        case   0: return True             # noqa: True
        case   _: proc.check_returncode() # noqa: True


_scripts_path: None | Path = None
def get_scripts_path() -> Path:
    global _scripts_path
    if _scripts_path is None:
        _scripts_path = get_env_crate_path() / "src" / "bin"
        _scripts_path.mkdir(exist_ok=True, parents=True)
    return _scripts_path


class BuildProfile(enum.Enum):
    RELEASE = "release"
    DEBUG = "debug"


def build_script(
    script_name: AnyPath,
    profile: BuildProfile = BuildProfile.RELEASE
) -> None:
    sp.run(
        ["cargo", "build", "--" + profile.value, "--bin", script_name],
        cwd=get_env_crate_path()
    )


def run_script(
    script_name: str,
    script_args: list[str] | None = None,
    profile: BuildProfile = BuildProfile.RELEASE,
) -> None:
    bin_path = get_env_crate_path() / "target" / profile.value / script_name
                            # This checks for None AND len() == 0
    exec_args = [bin_path] if not script_args else [bin_path] + script_args
    os.execvp(bin_path, exec_args)


def main(input_file: str, script_args: list[str] | None = None) -> None:
    file = Path(input_file)
    script_name = file.with_suffix("").name
    try_init_crate(get_env_crate_path())
    shutil.copy2(file, get_scripts_path())
    build_script(script_name)
    run_script(script_name, script_args)


def get_args(source: list[str] | None = None) -> ap.Namespace:
    parser = ap.ArgumentParser(
        description="Use as a shebang line to run rust source file as scripts")
    parser.add_argument("input_file",
        help="The rust source file to run as a script")
    parser.add_argument("script_args", nargs='*',
        help="Arguments to be passed to the rust script")

    return parser.parse_args(args=source)


def cli() -> None:
    main(**vars(get_args()))


def shebang() -> None:
    main(**vars(get_args(source=["--"] + sys.argv[1:])))


if __name__ == "__main__":
    cli()

