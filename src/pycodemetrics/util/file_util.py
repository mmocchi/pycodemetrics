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


def get_target_files_by_path(
    path: Path, exclude_patterns: list[str] | None = None
) -> list[Path]:
    """
    Get the target files by the specified path.

    Args:
        path (Path): The path to the target file or directory.
        exclude_patterns (list[str] | None): The exclude patterns.

    Returns:
        list[Path]: The list of target files.
    """
    if exclude_patterns is None:
        exclude_patterns = []

    if path.is_dir():
        all_files = [
            Path(p)
            for p in glob.glob(
                os.path.join(path.as_posix(), "**", "*.py"), recursive=True
            )
        ]
        return [f for f in all_files if not _is_excluded(f, exclude_patterns)]

    if path.is_file() and path.suffix == ".py":
        if _is_excluded(path, exclude_patterns):
            return []
        return [path]

    raise ValueError(f"Invalid path: {path}")


def get_target_files_by_git_ls_files(
    repo_path: Path, exclude_patterns: list[str] | None = None
) -> list[Path]:
    """
    Get the target files by the git ls-files command.

    Args:
        repo_path (Path): The path to the git repository.
        exclude_patterns (list[str] | None): The exclude patterns.

    Returns:
        list[Path]: The list of target files.
    """
    if exclude_patterns is None:
        exclude_patterns = []

    all_files = [f for f in list_git_files(repo_path) if f.suffix == ".py"]
    return [f for f in all_files if not _is_excluded(f, exclude_patterns)]


def _is_excluded(filepath: Path, exclude_patterns: list[str]) -> bool:
    """
    Check whether the file path should be excluded.

    Args:
        filepath (Path): The file path.
        exclude_patterns (list[str]): The exclude patterns.

    Returns:
        bool: True if the file path should be excluded, otherwise False.
    """
    file_str = filepath.as_posix()
    return any(
        fnmatch.fnmatch(file_str, pattern)
        or fnmatch.fnmatch(str(filepath), pattern)
        or pattern in file_str.split("/")
        for pattern in exclude_patterns
    )


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
