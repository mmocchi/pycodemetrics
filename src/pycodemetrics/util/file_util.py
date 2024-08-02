import glob
import os
from pathlib import Path

from pycodemetrics.gitclient.gitcli import list_git_files


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
