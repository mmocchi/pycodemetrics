from pathlib import Path

import pytest

from pycodemetrics.util.file_util import (
    _is_excluded,
    get_target_files_by_git_ls_files,
    get_target_files_by_path,
)


# Test for get_target_files_by_path using tmpdir
def test_get_target_files_by_path_directory(tmpdir):
    """
    get_target_files_by_path関数がディレクトリ内のPythonファイルのみを正しく返すことをテストします。
    """
    # Arrange
    tmpdir = Path(tmpdir)
    subdir = tmpdir.joinpath("subdir")
    subdir.mkdir()
    subdir.joinpath("test1.py").touch()
    subdir.joinpath("test2.py").touch()
    subdir.joinpath("test3.txt").touch()

    # Act
    result = get_target_files_by_path(tmpdir)

    # Assert
    expected_files = [
        subdir.joinpath("test1.py"),
        subdir.joinpath("test2.py"),
    ]
    assert sorted(result) == sorted(expected_files)


def test_get_target_files_by_path_file(tmpdir):
    """
    get_target_files_by_path関数が単一のPythonファイルを正しく返すことをテストします。
    """
    # Arrange
    tmpdir = Path(tmpdir)
    file = tmpdir.joinpath("test_file.py")
    file.touch()

    # Act
    result = get_target_files_by_path(file)

    # Assert
    assert result == [file]


def test_get_target_files_by_path_invalid(tmpdir):
    """
    get_target_files_by_path関数が存在しないパスを渡されたときにValueErrorを発生させることをテストします。
    """
    # Arrange
    tmpdir = Path(tmpdir)
    invalid_path = tmpdir.joinpath("invalid_path")

    # Act & Assert
    with pytest.raises(ValueError, match=f"Invalid path: {invalid_path.as_posix()}"):
        get_target_files_by_path(invalid_path)


# Test for get_target_files_by_git_ls_files
def test_get_target_files_by_git_ls_files(mocker):
    """
    get_target_files_by_git_ls_files関数がGitリポジトリ内のPythonファイルのみを正しく返すことをテストします。
    """
    # Arrange
    mocker.patch(
        "pycodemetrics.util.file_util.list_git_files",
        return_value=[
            Path("file1.py"),
            Path("file2.txt"),
            Path("file3.py"),
            Path("file4.py"),
        ],
    )

    # Act
    result = get_target_files_by_git_ls_files(Path("some/repo"))

    # Assert
    assert result == [Path("file1.py"), Path("file3.py"), Path("file4.py")]


class TestIsExcluded:
    """Test cases for _is_excluded function."""

    def test_is_excluded_with_exact_match(self):
        """Test _is_excluded with exact filename match."""
        filepath = Path("/src/project/.venv/lib/python.py")
        exclude_patterns = [".venv"]
        assert _is_excluded(filepath, exclude_patterns) is True

    def test_is_excluded_with_glob_pattern(self):
        """Test _is_excluded with glob pattern matching."""
        filepath = Path("/src/project/__pycache__/module.pyc")
        exclude_patterns = ["__pycache__"]
        assert _is_excluded(filepath, exclude_patterns) is True

    def test_is_excluded_with_wildcard_pattern(self):
        """Test _is_excluded with wildcard pattern."""
        filepath = Path("/src/project/build/output.py")
        exclude_patterns = ["build"]
        assert _is_excluded(filepath, exclude_patterns) is True

    def test_is_excluded_with_multiple_patterns(self):
        """Test _is_excluded with multiple exclude patterns."""
        filepath = Path("/src/project/node_modules/package.py")
        exclude_patterns = [".venv", "node_modules", "__pycache__"]
        assert _is_excluded(filepath, exclude_patterns) is True

    def test_is_excluded_not_matched(self):
        """Test _is_excluded returns False when no patterns match."""
        filepath = Path("/src/project/main.py")
        exclude_patterns = [".venv", "node_modules", "__pycache__"]
        assert _is_excluded(filepath, exclude_patterns) is False

    def test_is_excluded_empty_patterns(self):
        """Test _is_excluded with empty exclude patterns."""
        filepath = Path("/src/project/main.py")
        exclude_patterns = []
        assert _is_excluded(filepath, exclude_patterns) is False

    def test_is_excluded_with_nested_path(self):
        """Test _is_excluded with deeply nested paths."""
        filepath = Path("/src/project/.venv/lib/python3.10/site-packages/module.py")
        exclude_patterns = [".venv"]
        assert _is_excluded(filepath, exclude_patterns) is True

    def test_is_excluded_case_sensitive(self):
        """Test _is_excluded is case sensitive."""
        filepath = Path("/src/project/ENV/bin/python.py")
        exclude_patterns = ["env"]  # lowercase
        assert _is_excluded(filepath, exclude_patterns) is False

        exclude_patterns = ["ENV"]  # uppercase
        assert _is_excluded(filepath, exclude_patterns) is True


class TestGetTargetFilesWithExclusion:
    """Test cases for file targeting functions with exclusion patterns."""

    def test_get_target_files_by_path_with_exclusion(self, tmpdir):
        """Test get_target_files_by_path with exclusion patterns."""
        # Arrange
        tmpdir = Path(tmpdir)

        # Create directory structure
        venv_dir = tmpdir / ".venv" / "lib"
        venv_dir.mkdir(parents=True)
        cache_dir = tmpdir / "__pycache__"
        cache_dir.mkdir()
        src_dir = tmpdir / "src"
        src_dir.mkdir()

        # Create files
        (venv_dir / "excluded.py").touch()
        (cache_dir / "cached.py").touch()
        (src_dir / "main.py").touch()
        (tmpdir / "app.py").touch()

        # Act
        exclude_patterns = [".venv", "__pycache__"]
        result = get_target_files_by_path(tmpdir, exclude_patterns)

        # Assert
        expected_files = [src_dir / "main.py", tmpdir / "app.py"]
        assert sorted(result) == sorted(expected_files)

    def test_get_target_files_by_path_no_exclusion(self, tmpdir):
        """Test get_target_files_by_path without exclusion patterns."""
        # Arrange
        tmpdir = Path(tmpdir)
        subdir = tmpdir / "subdir"
        subdir.mkdir()
        (subdir / "test1.py").touch()
        (subdir / "test2.py").touch()

        # Act
        result = get_target_files_by_path(tmpdir, None)

        # Assert
        expected_files = [subdir / "test1.py", subdir / "test2.py"]
        assert sorted(result) == sorted(expected_files)

    def test_get_target_files_by_path_exclude_single_file(self, tmpdir):
        """Test get_target_files_by_path excludes single file when matched."""
        # Arrange
        tmpdir = Path(tmpdir)
        venv_file = tmpdir / ".venv" / "script.py"
        venv_file.parent.mkdir()
        venv_file.touch()

        # Act
        exclude_patterns = [".venv"]
        result = get_target_files_by_path(venv_file, exclude_patterns)

        # Assert
        assert result == []

    def test_get_target_files_by_git_ls_files_with_exclusion(self, mocker):
        """Test get_target_files_by_git_ls_files with exclusion patterns."""
        # Arrange
        mocker.patch(
            "pycodemetrics.util.file_util.list_git_files",
            return_value=[
                Path("src/main.py"),
                Path(".venv/lib/module.py"),
                Path("__pycache__/cached.py"),
                Path("tests/test_main.py"),
            ],
        )

        # Act
        exclude_patterns = [".venv", "__pycache__"]
        result = get_target_files_by_git_ls_files(Path("repo"), exclude_patterns)

        # Assert
        expected_files = [Path("src/main.py"), Path("tests/test_main.py")]
        assert sorted(result) == sorted(expected_files)
