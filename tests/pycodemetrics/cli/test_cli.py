import pytest
from click.testing import CliRunner

from pycodemetrics.cli import RETURN_CODE
from pycodemetrics.cli.analyze_python.handler import DisplayFormat
from pycodemetrics.cli.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_analyze_help(runner):
    """CLIのanalyzeコマンドのヘルプ表示が正常に動作することを確認する。

    Arrange:
        CLIランナーを準備

    Act:
        analyze --helpコマンドを実行

    Assert:
        終了コードが0であることを確認
        ヘルプメッセージが含まれていることを確認
    """
    # Arrange: CLIランナーは既に準備済み

    # Act: analyze --helpコマンドを実行
    result = runner.invoke(cli, ["analyze", "--help"])

    # Assert: 正常終了とヘルプメッセージの確認
    assert result.exit_code == 0
    assert "Analyze python metrics in the specified path" in result.output


def test_cli_analyze_invalid_path(runner):
    """存在しないパスを指定した場合にエラーが適切に処理されることを確認する。

    Arrange:
        CLIランナーを準備
        存在しないパスを用意

    Act:
        存在しないパスでanalyzeコマンドを実行

    Assert:
        エラー終了コード（2）であることを確認
        エラーメッセージが含まれていることを確認
    """
    # Arrange: CLIランナーは既に準備済み、存在しないパスを定義
    non_existent_path = "/non/existent/path"

    # Act: 存在しないパスでanalyzeコマンドを実行
    result = runner.invoke(cli, ["analyze", non_existent_path])

    # Assert: エラー終了とエラーメッセージの確認
    assert result.exit_code == 2
    assert "Error" in result.output


def test_cli_analyze_invalid_option(runner):
    """無効なオプションを指定した場合にエラーが適切に処理されることを確認する。

    Arrange:
        CLIランナーを準備

    Act:
        無効なオプションでanalyzeコマンドを実行

    Assert:
        エラー終了コード（2）であることを確認
        エラーメッセージが含まれていることを確認
    """
    # Arrange: CLIランナーは既に準備済み

    # Act: 無効なオプションでanalyzeコマンドを実行
    result = runner.invoke(cli, ["analyze", "--invalid-option"])

    # Assert: エラー終了とエラーメッセージの確認
    assert result.exit_code == 2
    assert "Error" in result.output


def test_cli_analyze_valid_path(runner, tmp_path):
    """有効なパスを指定した場合にanalyzeコマンドが正常に実行されることを確認する。

    Arrange:
        CLIランナーを準備
        テスト用のPythonファイルを作成

    Act:
        作成したディレクトリでanalyzeコマンドを実行

    Assert:
        正常終了コードであることを確認
        ファイル名が出力に含まれていることを確認
    """
    # Arrange: テスト用のPythonファイルを作成
    test_file = tmp_path / "test.py"
    test_file.write_text("def test_function():\n    pass\n")

    # Act: 作成したディレクトリでanalyzeコマンドを実行
    result = runner.invoke(cli, ["analyze", str(tmp_path)])

    # Assert: 正常終了とファイル名の確認
    assert result.exit_code == RETURN_CODE.SUCCESS
    assert "test.py" in result.output


@pytest.mark.parametrize(
    "format", [DisplayFormat.TABLE, DisplayFormat.CSV, DisplayFormat.JSON]
)
def test_cli_analyze_with_format(runner, tmp_path, format):
    """異なる出力フォーマット（TABLE、CSV、JSON）でanalyzeコマンドが正常に実行されることを確認する。

    Arrange:
        CLIランナーを準備
        テスト用のPythonファイルを作成
        フォーマットパラメータを用意

    Act:
        指定したフォーマットでanalyzeコマンドを実行

    Assert:
        正常終了コードであることを確認
    """
    # Arrange: テスト用のPythonファイルを作成
    test_file = tmp_path / "test.py"
    test_file.write_text("def test_function():\n    pass\n")

    # Act: 指定したフォーマットでanalyzeコマンドを実行
    result = runner.invoke(cli, ["analyze", str(tmp_path), "--format", format.value])

    # Assert: 正常終了の確認
    assert result.exit_code == RETURN_CODE.SUCCESS


def test_cli_analyze_with_export(runner, tmp_path):
    """--exportオプションを使用してファイル出力が正常に行われることを確認する。

    Arrange:
        CLIランナーを準備
        テスト用のPythonファイルを作成
        エクスポート先ファイルパスを用意

    Act:
        --exportオプション付きでanalyzeコマンドを実行

    Assert:
        正常終了コードであることを確認
        エクスポートファイルが作成されていることを確認
    """
    # Arrange: テスト用のPythonファイルとエクスポート先を準備
    test_file = tmp_path / "test.py"
    test_file.write_text("def test_function():\n    pass\n")
    export_file = tmp_path / "output.csv"

    # Act: --exportオプション付きでanalyzeコマンドを実行
    result = runner.invoke(
        cli, ["analyze", str(tmp_path), "--export", str(export_file)]
    )

    # Assert: 正常終了とファイル作成の確認
    assert result.exit_code == RETURN_CODE.SUCCESS
    assert export_file.exists()


def test_cli_analyze_with_export_overwrite(runner, tmp_path):
    """--export-overwriteオプションを使用して既存ファイルの上書きが正常に行われることを確認する。

    Arrange:
        CLIランナーを準備
        テスト用のPythonファイルを作成
        既存のエクスポートファイルを作成

    Act:
        --export-overwriteオプション付きでanalyzeコマンドを実行

    Assert:
        正常終了コードであることを確認
        エクスポートファイルが存在することを確認
        ファイル内容が上書きされていることを確認
    """
    # Arrange: テスト用のPythonファイルと既存エクスポートファイルを準備
    test_file = tmp_path / "test.py"
    test_file.write_text("def test_function():\n    pass\n")
    export_file = tmp_path / "output.csv"
    export_file.write_text("existing content")

    # Act: --export-overwriteオプション付きでanalyzeコマンドを実行
    result = runner.invoke(
        cli,
        ["analyze", str(tmp_path), "--export", str(export_file), "--export-overwrite"],
    )

    # Assert: 正常終了とファイル上書きの確認
    assert result.exit_code == RETURN_CODE.SUCCESS
    assert export_file.exists()
    assert export_file.read_text() != "existing content"
