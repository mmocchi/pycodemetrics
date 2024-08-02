import glob
import os

from pycodemetrics.gitclient.gitcli import list_git_files


def get_target_files_by_path(path: str) -> list[str]:
    if os.path.isdir(path):
        return glob.glob(os.path.join(path, "**", "*.py"), recursive=True)

    if os.path.isfile(path) and path.endswith(".py"):
        return [path]

    raise ValueError(f"Invalid path: {path}")


def get_target_files_by_git_ls_files(repo_path: str) -> list[str]:
    return [f for f in list_git_files(repo_path) if f.endswith(".py")]
