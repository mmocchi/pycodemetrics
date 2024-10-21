import fnmatch
import glob
import os
from enum import Enum
from pathlib import Path

from pycodemetrics.config.config_manager import UserGroupConfig
from pycodemetrics.gitclient.gitcli import list_git_files


class CodeType(Enum):
    """
    Code type.

    PRODUCT: Product code.
    TEST: Test code.
    """

    PRODUCT = "product"
    TEST = "test"


def get_target_files_by_path(path: Path) -> list[Path]:
    """
    Get the target files by the specified path.

    Args:
        path (Path): The path to the target file or directory.

    Returns:
        list[Path]: The list of target files.
    """
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
    """
    Get the target files by the git ls-files command.

    Args:
        repo_path (Path): The path to the git repository.

    Returns:
        list[Path]: The list of target files.
    """
    return [f for f in list_git_files(repo_path) if f.suffix == ".py"]


def _is_match(
    filepath: Path,
    patterns: list[str],
) -> bool:
    """
    Check whether the file path matches the patterns.

    Args:
        filepath (Path): The file path.
        patterns (list[str]): The patterns.

    Returns:
        bool: True if the file path matches the patterns, otherwise False.
    """
    return any(fnmatch.fnmatch(filepath.as_posix(), pattern) for pattern in patterns)


def get_code_type(filepath: Path, patterns: list[str]) -> CodeType:
    """
    Get the code type by the specified file path.

    Args:
        filepath (Path): The file path.
        patterns (list[str]): The patterns.

    Returns:
        CodeType: The code type.
    """
    if _is_match(filepath, patterns):
        return CodeType.TEST
    return CodeType.PRODUCT


def get_group_name(filepath: Path, user_groups: list[UserGroupConfig]) -> str:
    """
    Get the group name by the specified file path.

    Args:
        filepath (Path): The file path.
        user_groups (list[UserGroupConfig]): The user groups.

    Returns:
        str: The group name. if the group name is not found, return "undefined".
    """
    for group in user_groups:
        if _is_match(filepath, group.patterns):
            return group.name
    return "undefined"
