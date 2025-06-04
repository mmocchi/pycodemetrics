"""gitcli.pyのテストモジュール。"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pycodemetrics.gitclient.gitcli import (
    _check_git_repo,
    _run_command,
    get_file_gitlogs,
    get_gitlogs,
    list_git_files,
)


class TestCheckGitRepo:
    """_check_git_repo関数のテストクラス。"""

    def test_check_git_repo_valid(self) -> None:
        """有効なGitリポジトリのテスト。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            git_dir = repo_path / ".git"
            git_dir.mkdir()

            # 例外が発生しないことを確認
            _check_git_repo(repo_path)

    def test_check_git_repo_invalid(self) -> None:
        """無効なGitリポジトリのテスト。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            with pytest.raises(ValueError, match="Not a git repository"):
                _check_git_repo(repo_path)


class TestRunCommand:
    """_run_command関数のテストクラス。"""

    @patch("subprocess.Popen")
    def test_run_command_success(self, mock_popen: MagicMock) -> None:
        """コマンド成功時のテスト。"""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"line1\nline2\nline3", b"")
        mock_popen.return_value = mock_process

        result = _run_command("echo test", Path("/tmp"))

        assert result == ["line1", "line2", "line3"]
        mock_popen.assert_called_once()

    @patch("subprocess.Popen")
    def test_run_command_failure(self, mock_popen: MagicMock) -> None:
        """コマンド失敗時のテスト。"""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.communicate.return_value = (b"", b"Error message")
        mock_popen.return_value = mock_process

        with pytest.raises(ValueError, match="Error running command"):
            _run_command("false", Path("/tmp"))

    @patch("subprocess.Popen")
    def test_run_command_timeout(self, mock_popen: MagicMock) -> None:
        """コマンドタイムアウト時のテスト。"""
        mock_process = MagicMock()
        mock_process.communicate.side_effect = subprocess.TimeoutExpired("cmd", 1)
        mock_popen.return_value = mock_process

        with pytest.raises(TimeoutError, match="Timeout running command"):
            _run_command("sleep 10", Path("/tmp"), timeout_seconds=1)

        mock_process.kill.assert_called_once()

    @patch("subprocess.Popen")
    def test_run_command_with_timeout_success(self, mock_popen: MagicMock) -> None:
        """タイムアウト指定でコマンド成功時のテスト。"""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"output", b"")
        mock_popen.return_value = mock_process

        result = _run_command("echo test", Path("/tmp"), timeout_seconds=5)

        assert result == ["output"]
        mock_process.communicate.assert_called_with(timeout=5)

    @patch("subprocess.Popen")
    def test_run_command_custom_encoding(self, mock_popen: MagicMock) -> None:
        """カスタムエンコーディング指定時のテスト。"""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = ("テスト".encode("shift_jis"), b"")
        mock_popen.return_value = mock_process

        result = _run_command("echo test", Path("/tmp"), encording="shift_jis")

        assert result == ["テスト"]


class TestListGitFiles:
    """list_git_files関数のテストクラス。"""

    @patch("pycodemetrics.gitclient.gitcli._check_git_repo")
    @patch("pycodemetrics.gitclient.gitcli._run_command")
    def test_list_git_files_success(
        self, mock_run_command: MagicMock, mock_check_git_repo: MagicMock
    ) -> None:
        """git ls-files成功時のテスト。"""
        mock_run_command.return_value = ["file1.py", "file2.py", "file3.txt", ""]

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            result = list_git_files(repo_path)

            assert result == [
                Path("file1.py"),
                Path("file2.py"),
                Path("file3.txt"),
                Path(""),
            ]
            mock_check_git_repo.assert_called_once_with(repo_path)
            mock_run_command.assert_called_once_with("git ls-files", repo_path, "utf-8")

    @patch("pycodemetrics.gitclient.gitcli._check_git_repo")
    @patch("pycodemetrics.gitclient.gitcli._run_command")
    def test_list_git_files_default_path(
        self, mock_run_command: MagicMock, mock_check_git_repo: MagicMock
    ) -> None:
        """デフォルトパス（現在のディレクトリ）でのテスト。"""
        mock_run_command.return_value = ["test.py"]

        with patch("pathlib.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("/current/dir")
            result = list_git_files()

            assert result == [Path("test.py")]
            mock_check_git_repo.assert_called_once_with(Path("/current/dir"))

    @patch("pycodemetrics.gitclient.gitcli._check_git_repo")
    def test_list_git_files_not_git_repo(self, mock_check_git_repo: MagicMock) -> None:
        """Gitリポジトリでない場合のテスト。"""
        mock_check_git_repo.side_effect = ValueError("Not a git repository")

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            with pytest.raises(ValueError, match="Not a git repository"):
                list_git_files(repo_path)


class TestGetFileGitlogs:
    """get_file_gitlogs関数のテストクラス。"""

    @patch("pycodemetrics.gitclient.gitcli._check_git_repo")
    @patch("pycodemetrics.gitclient.gitcli._run_command")
    def test_get_file_gitlogs_success(
        self, mock_run_command: MagicMock, mock_check_git_repo: MagicMock
    ) -> None:
        """ファイルのgitログ取得成功時のテスト。"""
        mock_run_command.return_value = [
            "abc123,John Doe,2023-01-01 10:00:00 +0000,Initial commit",
            "def456,Jane Smith,2023-01-02 11:00:00 +0000,Fix bug",
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            file_path = Path("test.py")

            result = get_file_gitlogs(file_path, repo_path)

            assert len(result) == 2
            assert "abc123,John Doe" in result[0]
            assert "def456,Jane Smith" in result[1]
            mock_check_git_repo.assert_called_once_with(repo_path)
            mock_run_command.assert_called_once_with(
                f"git log --pretty=format:'%h,%aN,%ad,%s' --date=iso -- {file_path}",
                repo_path,
                "utf-8",
            )

    @patch("pycodemetrics.gitclient.gitcli._check_git_repo")
    @patch("pycodemetrics.gitclient.gitcli._run_command")
    def test_get_file_gitlogs_default_path(
        self, mock_run_command: MagicMock, mock_check_git_repo: MagicMock
    ) -> None:
        """デフォルトパスでのファイルgitログ取得テスト。"""
        mock_run_command.return_value = ["commit1"]

        with patch("pathlib.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("/current/dir")
            file_path = Path("test.py")

            result = get_file_gitlogs(file_path)

            assert result == ["commit1"]
            mock_check_git_repo.assert_called_once_with(Path("/current/dir"))


class TestGetGitlogs:
    """get_gitlogs関数のテストクラス。"""

    @patch("pycodemetrics.gitclient.gitcli._check_git_repo")
    @patch("pycodemetrics.gitclient.gitcli._run_command")
    def test_get_gitlogs_success(
        self, mock_run_command: MagicMock, mock_check_git_repo: MagicMock
    ) -> None:
        """全gitログ取得成功時のテスト。"""
        mock_run_command.return_value = [
            "abc123,John Doe,2023-01-01 10:00:00 +0000,Initial commit",
            "def456,Jane Smith,2023-01-02 11:00:00 +0000,Add feature",
            "ghi789,Bob Wilson,2023-01-03 12:00:00 +0000,Fix bug",
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            result = get_gitlogs(repo_path)

            assert len(result) == 3
            assert "abc123,John Doe" in result[0]
            assert "def456,Jane Smith" in result[1]
            assert "ghi789,Bob Wilson" in result[2]
            mock_check_git_repo.assert_called_once_with(repo_path)
            mock_run_command.assert_called_once_with(
                "git log --pretty=format:'%h,%aN,%ad,%s' --date=iso", repo_path, "utf-8"
            )

    @patch("pycodemetrics.gitclient.gitcli._check_git_repo")
    @patch("pycodemetrics.gitclient.gitcli._run_command")
    def test_get_gitlogs_default_path(
        self, mock_run_command: MagicMock, mock_check_git_repo: MagicMock
    ) -> None:
        """デフォルトパスでの全gitログ取得テスト。"""
        mock_run_command.return_value = ["commit1", "commit2"]

        with patch("pathlib.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("/current/dir")

            result = get_gitlogs()

            assert result == ["commit1", "commit2"]
            mock_check_git_repo.assert_called_once_with(Path("/current/dir"))

    @patch("pycodemetrics.gitclient.gitcli._check_git_repo")
    @patch("pycodemetrics.gitclient.gitcli._run_command")
    def test_get_gitlogs_custom_encoding(
        self, mock_run_command: MagicMock, mock_check_git_repo: MagicMock
    ) -> None:
        """カスタムエンコーディングでのgitログ取得テスト。"""
        mock_run_command.return_value = ["commit1"]

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            result = get_gitlogs(repo_path, encoding="shift_jis")

            assert result == ["commit1"]
            mock_run_command.assert_called_once_with(
                "git log --pretty=format:'%h,%aN,%ad,%s' --date=iso",
                repo_path,
                "shift_jis",
            )
