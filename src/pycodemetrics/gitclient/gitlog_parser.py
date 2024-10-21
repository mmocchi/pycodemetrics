import datetime as dt
import logging
from pathlib import Path

from pycodemetrics.gitclient.models import GitFileCommitLog

logger = logging.getLogger(__name__)


def parse_gitlogs(git_file_path: Path, gitlogs: list[str]) -> list[GitFileCommitLog]:
    """
    Parse the git logs and return a list of logs.

    Args:
        git_file_path (Path): The path to the git file.
        gitlogs (list[str]): The git logs.

    Returns:
        list[GitFileCommitLog]: The parsed git logs.
    """
    if len(gitlogs) == 0:
        return []

    parsed_logs = []

    for log in gitlogs:
        try:
            commit_hash, author, commit_date, message = log.split(",", maxsplit=3)
        except ValueError:
            logger.warning(f"Failed to parse the log: {log}. file: {git_file_path}")
            continue

        # commit_date を datetime に変換
        commit_date_dt = dt.datetime.strptime(commit_date, "%Y-%m-%d %H:%M:%S %z")

        parsed_logs.append(
            GitFileCommitLog(
                filepath=git_file_path,
                commit_hash=commit_hash,
                author=author,
                commit_date=commit_date_dt.astimezone(),
                message=message,
            )
        )
    return parsed_logs
