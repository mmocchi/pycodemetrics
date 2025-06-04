"""changecount.pyのテストモジュール。"""

from collections import Counter
from datetime import datetime
from pathlib import Path

from pycodemetrics.gitclient.models import GitFileCommitLog
from pycodemetrics.metrics.changecount import calculate_changecount


class TestCalculateChangecount:
    """calculate_changecount関数のテストクラス。"""

    def test_calculate_changecount_empty_list(self) -> None:
        """空のリストでchangecountを計算するテスト。"""
        result = calculate_changecount([])
        assert result == Counter()

    def test_calculate_changecount_single_author(self) -> None:
        """単一のAuthorでchangecountを計算するテスト。"""
        gitlogs = [
            GitFileCommitLog(
                filepath=Path("test.py"),
                commit_hash="abc123",
                author="John Doe",
                commit_date=datetime(2023, 1, 1),
                message="Initial commit",
            )
        ]

        result = calculate_changecount(gitlogs)
        expected = Counter({"John Doe": 1})
        assert result == expected

    def test_calculate_changecount_multiple_authors(self) -> None:
        """複数のAuthorでchangecountを計算するテスト。"""
        gitlogs = [
            GitFileCommitLog(
                filepath=Path("test1.py"),
                commit_hash="abc123",
                author="John Doe",
                commit_date=datetime(2023, 1, 1),
                message="Initial commit",
            ),
            GitFileCommitLog(
                filepath=Path("test2.py"),
                commit_hash="def456",
                author="Jane Smith",
                commit_date=datetime(2023, 1, 2),
                message="Add feature",
            ),
            GitFileCommitLog(
                filepath=Path("test3.py"),
                commit_hash="ghi789",
                author="John Doe",
                commit_date=datetime(2023, 1, 3),
                message="Fix bug",
            ),
        ]

        result = calculate_changecount(gitlogs)
        expected = Counter({"John Doe": 2, "Jane Smith": 1})
        assert result == expected

    def test_calculate_changecount_same_author_multiple_commits(self) -> None:
        """同一Authorの複数コミットでchangecountを計算するテスト。"""
        gitlogs = [
            GitFileCommitLog(
                filepath=Path("test1.py"),
                commit_hash="abc123",
                author="John Doe",
                commit_date=datetime(2023, 1, 1),
                message="Initial commit",
            ),
            GitFileCommitLog(
                filepath=Path("test2.py"),
                commit_hash="def456",
                author="John Doe",
                commit_date=datetime(2023, 1, 2),
                message="Second commit",
            ),
            GitFileCommitLog(
                filepath=Path("test3.py"),
                commit_hash="ghi789",
                author="John Doe",
                commit_date=datetime(2023, 1, 3),
                message="Third commit",
            ),
        ]

        result = calculate_changecount(gitlogs)
        expected = Counter({"John Doe": 3})
        assert result == expected

    def test_calculate_changecount_special_characters_in_author(self) -> None:
        """Author名に特殊文字が含まれる場合のテスト。"""
        gitlogs = [
            GitFileCommitLog(
                filepath=Path("test.py"),
                commit_hash="abc123",
                author="山田 太郎",
                commit_date=datetime(2023, 1, 1),
                message="Initial commit",
            ),
            GitFileCommitLog(
                filepath=Path("test2.py"),
                commit_hash="def456",
                author="O'Connor, Patrick",
                commit_date=datetime(2023, 1, 2),
                message="Add feature",
            ),
        ]

        result = calculate_changecount(gitlogs)
        expected = Counter({"山田 太郎": 1, "O'Connor, Patrick": 1})
        assert result == expected

    def test_calculate_changecount_preserves_counter_type(self) -> None:
        """返り値がCounterオブジェクトであることをテスト。"""
        gitlogs = [
            GitFileCommitLog(
                filepath=Path("test.py"),
                commit_hash="abc123",
                author="John Doe",
                commit_date=datetime(2023, 1, 1),
                message="Initial commit",
            )
        ]

        result = calculate_changecount(gitlogs)
        assert isinstance(result, Counter)
        assert result.most_common(1) == [("John Doe", 1)]
