import os
import subprocess


def list_git_files(git_repo_path: str | None = None) -> list[str]:
    """
    List all the files in the current repository.
    """
    git_repo_path = git_repo_path or "."

    if not os.path.exists(os.path.join(git_repo_path, ".git")):
        raise ValueError("Not a git repository")

    cmd = "git ls-files"
    p = subprocess.Popen(cmd, cwd=git_repo_path, shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    out = out.decode("utf-8")
    return out.split("\n")


def get_gitlogs(git_file_path, git_repo_path: str | None = None) -> str:
    """
    Get the git logs for the current repository.
    """
    git_repo_path = git_repo_path or "."

    if not os.path.exists(os.path.join(git_repo_path, ".git")):
        raise ValueError("Not a git repository")

    cmd = f"git log --pretty=format:'%h,%aN,%ad,%s' --date=iso -- {git_file_path}"
    p = subprocess.Popen(cmd, cwd=git_repo_path, shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    out = out.decode("utf-8")
    return out
