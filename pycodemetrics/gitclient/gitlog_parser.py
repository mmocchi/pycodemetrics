from pycodemetrics.gitclient.gitcli import get_gitlogs, list_git_files
from pycodemetrics.gitclient.models import GitFileCommitLog


def parse_gitlogs(git_file_path: str, gitlogs: str) -> list[GitFileCommitLog]:
    """
    Parse the git logs and return a list of logs.
    """
    logs = gitlogs.split("\n")

    parsed_logs = []

    for log in logs:
        commit_hash, author, commit_date, message = log.split(",")
        parsed_logs.append(
            GitFileCommitLog(
                filepath=git_file_path,
                commit_hash=commit_hash,
                author=author,
                commit_date=commit_date,
                message=message,
            )
        )
    return parsed_logs


if __name__ == "__main__":
    for git_file_path in list_git_files():
        rawlog = get_gitlogs(git_file_path)
        parsed_logs = parse_gitlogs(git_file_path, rawlog)
        for parsed_log in parsed_logs:
            print(parsed_log)
