import fnmatch
import glob
import os
from enum import Enum
from pathlib import Path

from pycodemetrics.config.config_manager import UserGroupConfig
from pycodemetrics.gitclient.gitcli import list_git_files


class CodeType(Enum):
    PRODUCT = "product"
    TEST = "test"


def get_target_files_by_path(path: Path) -> list[Path]:
    if path.is_dir():
        return [
            Path(p)
            for p in glob.glob(
                os.path.join(path.as_posix(), "**", "*.py"), recursive=True
            )
        ]

    if path.is_file() and path.suffix == ".py":
        return [path]

    raise ValueError(f"Invalid path: {path}")


def get_target_files_by_git_ls_files(repo_path: Path) -> list[Path]:
    return [f for f in list_git_files(repo_path) if f.suffix == ".py"]


def _is_match(
    filepath: Path,
    patterns: list[str],
) -> bool:
    return any(fnmatch.fnmatch(filepath.as_posix(), pattern) for pattern in patterns)


def get_product_or_test(filepath: Path, patterns: list[str]) -> CodeType:
    if _is_match(filepath, patterns):
        return CodeType.TEST
    return CodeType.PRODUCT


def get_group_name(filepath: Path, user_groups: list[UserGroupConfig]) -> str:
    for group in user_groups:
        if _is_match(filepath, group.patterns):
            return group.name
    return "undefined"
