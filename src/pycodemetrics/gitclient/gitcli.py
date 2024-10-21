import subprocess
from pathlib import Path

RETURN_CODE_SUCCESS = 0


def _check_git_repo(git_repo_path: Path) -> None:
    """
    Check if the path is a git repository.

    Args:
        git_repo_path (Path): The path to the git repository.

    Raises:
        ValueError: If the path is not a git repository.
    """
    if not git_repo_path.joinpath(".git").exists():
        raise ValueError("Not a git repository")


def _run_command(
    cmd: str, current_dir: Path, encording: str = "utf-8", timeout_seconds: int = 0
) -> list[str]:
    """
    Run the command.

    Args:
        cmd (str): The command to run.
        current_dir (Path): The current directory.
        encording (str): The encoding.
        timeout_seconds (int): The timeout in seconds.

    Returns:
        list[str]: The output of the command.

    Raises:
        ValueError: If the command returns an error.
        TimeoutError: If the command times out.
    """
    p = subprocess.Popen(
        cmd,
        cwd=current_dir.as_posix(),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
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
    git_repo_path: Path | None = None, encoding: str = "utf-8"
) -> list[Path]:
    """
    List all the files in the current repository.
    result by `git ls-files`

    Args:
        git_repo_path (Path): The path to the git repository.
        encoding (str): The encoding.

    Returns:
        list[Path]: The list of file paths.
    """
    git_repo_path = git_repo_path or Path.cwd()

    _check_git_repo(git_repo_path)

    cmd = "git ls-files"
    return [Path(f) for f in _run_command(cmd, git_repo_path, encoding)]


def get_file_gitlogs(
    git_file_path: Path, git_repo_path: Path | None = None, encoding: str = "utf-8"
) -> list[str]:
    """
    Get the git logs for the current repository.

    Args:
        git_file_path (Path): The path to the file.
        git_repo_path (Path): The path to the git repository.
        encoding (str): The encoding.

    Returns:
        list[str]: The git logs.
    """
    git_repo_path = git_repo_path or Path.cwd()

    _check_git_repo(git_repo_path)

    cmd = f"git log --pretty=format:'%h,%aN,%ad,%s' --date=iso -- {git_file_path}"
    return _run_command(cmd, git_repo_path, encoding)


def get_gitlogs(
    git_repo_path: Path | None = None, encoding: str = "utf-8"
) -> list[str]:
    """
    Get the git logs for the current repository.

    Args:
        git_repo_path (Path): The path to the git repository.
        encoding (str): The encoding.

    Returns:
        list[str]: The git logs.
    """

    git_repo_path = git_repo_path or Path.cwd()

    _check_git_repo(git_repo_path)

    cmd = "git log --pretty=format:'%h,%aN,%ad,%s' --date=iso"
    return _run_command(cmd, git_repo_path, encoding)
