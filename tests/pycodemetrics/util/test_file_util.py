import os

import pytest
from pycodemetrics.util.file_util import (
    get_target_files_by_git_ls_files,
    get_target_files_by_path,
)


# Test for get_target_files_by_path using tmpdir
def test_get_target_files_by_path_directory(tmpdir):
    """
    get_target_files_by_path関数がディレクトリ内のPythonファイルのみを正しく返すことをテストします。
    """
    # Arrange
    subdir = tmpdir.mkdir("subdir")
    subdir.join("test1.py").write("")
    subdir.join("test2.py").write("")
    subdir.join("test3.txt").write("")

    # Act
    result = get_target_files_by_path(tmpdir.strpath)

    # Assert
    expected_files = [
        os.path.join(subdir.strpath, "test1.py"),
        os.path.join(subdir.strpath, "test2.py"),
    ]
    assert sorted(result) == sorted(expected_files)


def test_get_target_files_by_path_file(tmpdir):
    """
    get_target_files_by_path関数が単一のPythonファイルを正しく返すことをテストします。
    """
    # Arrange
    file = tmpdir.join("test_file.py")
    file.write("")

    # Act
    result = get_target_files_by_path(file.strpath)

    # Assert
    assert result == [file.strpath]


def test_get_target_files_by_path_invalid(tmpdir):
    """
    get_target_files_by_path関数が存在しないパスを渡されたときにValueErrorを発生させることをテストします。
    """
    # Arrange
    invalid_path = tmpdir.join("invalid_path")

    # Act & Assert
    with pytest.raises(ValueError, match=f"Invalid path: {invalid_path.strpath}"):
        get_target_files_by_path(invalid_path.strpath)


# Test for get_target_files_by_git_ls_files
def test_get_target_files_by_git_ls_files(mocker):
    """
    get_target_files_by_git_ls_files関数がGitリポジトリ内のPythonファイルのみを正しく返すことをテストします。
    """
    # Arrange
    mocker.patch(
        "pycodemetrics.util.file_util.list_git_files",
        return_value=["file1.py", "file2.txt", "file3.py", "file4.py"],
    )

    # Act
    result = get_target_files_by_git_ls_files("some/repo")

    # Assert
    assert result == ["file1.py", "file3.py", "file4.py"]
