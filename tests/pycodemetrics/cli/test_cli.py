import pytest
from click.testing import CliRunner

from pycodemetrics.cli import RETURN_CODE
from pycodemetrics.cli.analyze_python.handler import DisplayFormat
from pycodemetrics.cli.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_analyze_help(runner):
    result = runner.invoke(cli, ["analyze", "--help"])
    assert result.exit_code == 0
    assert "Analyze python metrics in the specified path" in result.output


def test_cli_analyze_invalid_path(runner):
    result = runner.invoke(cli, ["analyze", "/non/existent/path"])
    assert result.exit_code == 2
    assert "Error" in result.output


def test_cli_analyze_invalid_option(runner):
    result = runner.invoke(cli, ["analyze", "--invalid-option"])
    assert result.exit_code == 2
    assert "Error" in result.output


def test_cli_analyze_valid_path(runner, tmp_path):
    # Create a sample Python file
    test_file = tmp_path / "test.py"
    test_file.write_text("def test_function():\n    pass\n")

    result = runner.invoke(cli, ["analyze", str(tmp_path)])
    assert result.exit_code == RETURN_CODE.SUCCESS
    assert "test.py" in result.output


@pytest.mark.parametrize(
    "format", [DisplayFormat.TABLE, DisplayFormat.CSV, DisplayFormat.JSON]
)
def test_cli_analyze_with_format(runner, tmp_path, format):
    test_file = tmp_path / "test.py"
    test_file.write_text("def test_function():\n    pass\n")

    result = runner.invoke(cli, ["analyze", str(tmp_path), "--format", format.value])
    assert result.exit_code == RETURN_CODE.SUCCESS


def test_cli_analyze_with_export(runner, tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("def test_function():\n    pass\n")

    export_file = tmp_path / "output.csv"
    result = runner.invoke(
        cli, ["analyze", str(tmp_path), "--export", str(export_file)]
    )

    assert result.exit_code == RETURN_CODE.SUCCESS
    assert export_file.exists()


def test_cli_analyze_with_export_overwrite(runner, tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("def test_function():\n    pass\n")

    export_file = tmp_path / "output.csv"
    export_file.write_text("existing content")

    result = runner.invoke(
        cli,
        ["analyze", str(tmp_path), "--export", str(export_file), "--export-overwrite"],
    )

    assert result.exit_code == RETURN_CODE.SUCCESS
    assert export_file.exists()
    assert export_file.read_text() != "existing content"
