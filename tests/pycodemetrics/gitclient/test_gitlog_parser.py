import datetime as dt
from pathlib import Path

from pycodemetrics.gitclient.gitlog_parser import parse_gitlogs
from pycodemetrics.gitclient.models import GitFileCommitLog


def test_parse_gitlogs():
    """parse_gitlogs関数がGitログの文字列を正しくGitFileCommitLogオブジェクトのリストに変換することを確認する。

    Arrange:
        テスト用のファイルパスを準備
        テスト用のGitログの文字列リストを準備
        期待される結果のGitFileCommitLogオブジェクトリストを準備

    Act:
        parse_gitlogs関数を実行してGitログを解析

    Assert:
        解析結果が期待される結果と一致することを確認
        各ログエントリが正しくパースされていることを確認
        日時がタイムゾーン情報付きで正しく変換されていることを確認
    """
    # Arrange: テスト用のファイルパスとGitログデータを準備
    git_file_path = Path("path/to/file.py")
    gitlogs = [
        "abc123,John Doe,2023-10-01 12:00:00 +0000,Initial commit",
        "def456,Jane Smith,2023-10-02 13:30:00 +0000,Added new feature",
    ]

    # 期待される結果を準備
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

    # Act: parse_gitlogs関数を実行してGitログを解析
    actual_logs = parse_gitlogs(git_file_path, gitlogs)

    # Assert: 解析結果が期待される結果と一致することを確認
    assert actual_logs == expected_logs
