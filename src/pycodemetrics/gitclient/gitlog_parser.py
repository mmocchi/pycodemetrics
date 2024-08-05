import datetime as dt
from pathlib import Path

from pycodemetrics.gitclient.models import GitFileCommitLog


def parse_gitlogs(git_file_path: Path, gitlogs: list[str]) -> list[GitFileCommitLog]:
    """
    Parse the git logs and return a list of logs.
    """
    if len(gitlogs) == 0:
        return []

    parsed_logs = []

    for log in gitlogs:
        commit_hash, author, commit_date, message = log.split(",")

        # commit_date を datetime に変換
        commit_date_dt = dt.datetime.strptime(commit_date, "%Y-%m-%d %H:%M:%S %z")

        parsed_logs.append(
            GitFileCommitLog(
                filepath=git_file_path,
                commit_hash=commit_hash,
                author=author,
                commit_date=commit_date_dt,
                message=message,
            )
        )
    return parsed_logs
