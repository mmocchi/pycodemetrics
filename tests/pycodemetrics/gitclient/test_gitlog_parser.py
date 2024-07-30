import datetime as dt

from pycodemetrics.gitclient.gitlog_parser import parse_gitlogs
from pycodemetrics.gitclient.models import GitFileCommitLog


def test_parse_gitlogs():
    # Arrange
    git_file_path = "path/to/file.py"
    gitlogs = [
        "abc123,John Doe,2023-10-01 12:00:00 +0000,Initial commit",
        "def456,Jane Smith,2023-10-02 13:30:00 +0000,Added new feature",
    ]

    # Act
    actual_logs = parse_gitlogs(git_file_path, gitlogs)

    # 期待される結果
    expected_logs = [
        GitFileCommitLog(
            filepath=git_file_path,
            commit_hash="abc123",
            author="John Doe",
            commit_date=dt.datetime(2023, 10, 1, 12, 0, 0, tzinfo=dt.timezone.utc),
            message="Initial commit",
        ),
        GitFileCommitLog(
            filepath=git_file_path,
            commit_hash="def456",
            author="Jane Smith",
            commit_date=dt.datetime(2023, 10, 2, 13, 30, 0, tzinfo=dt.timezone.utc),
            message="Added new feature",
        ),
    ]

    # 実際の結果と期待される結果を比較
    assert actual_logs == expected_logs
