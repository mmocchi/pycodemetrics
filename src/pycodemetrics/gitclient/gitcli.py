import os
import subprocess

RETURN_CODE_SUCCESS = 0


def _check_git_repo(git_repo_path: str) -> None:
    if not os.path.exists(os.path.join(git_repo_path, ".git")):
        raise ValueError("Not a git repository")


def _run_command(
    cmd: str, cwd: str, encording: str = "utf-8", timeout_seconds: int = 0
) -> list[str]:
    p = subprocess.Popen(
        cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    try:
        if timeout_seconds > 0:
            out, err = p.communicate(timeout=timeout_seconds)
        else:
            out, err = p.communicate()
        if p.returncode != RETURN_CODE_SUCCESS:
            encoded_stderr = err.decode(encording)
            raise ValueError(f"Error running command: {cmd}, cause: {encoded_stderr}: ")

        encoded_stdout = out.decode(encording)
        return encoded_stdout.split("\n")
    except subprocess.TimeoutExpired:
        p.kill()
        raise TimeoutError(f"Timeout running command: {cmd}")


def list_git_files(
    git_repo_path: str | None = None, encoding: str = "utf-8"
) -> list[str]:
    """
    List all the files in the current repository.
    """
    git_repo_path = git_repo_path or "."

    _check_git_repo(git_repo_path)

    cmd = "git ls-files"
    return _run_command(cmd, git_repo_path, encoding)


def get_file_gitlogs(
    git_file_path, git_repo_path: str | None = None, encoding: str = "utf-8"
) -> list[str]:
    """
    Get the git logs for the current repository.
    """
    git_repo_path = git_repo_path or "."

    _check_git_repo(git_repo_path)

    cmd = f"git log --pretty=format:'%h,%aN,%ad,%s' --date=iso -- {git_file_path}"
    return _run_command(cmd, git_repo_path, encoding)


def get_gitlogs(git_repo_path: str | None = None, encoding: str = "utf-8") -> list[str]:
    git_repo_path = git_repo_path or "."

    _check_git_repo(git_repo_path)

    cmd = "git log --pretty=format:'%h,%aN,%ad,%s' --date=iso"
    return _run_command(cmd, git_repo_path, encoding)
