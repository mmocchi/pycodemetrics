from pathlib import Path

import pandas as pd
import pytest
from pycodemetrics.cli.analyze_python.handler import (
    DisplayFormat,
    DisplayParameter,
    ExportParameter,
    InputTargetParameter,
    _diplay,
    _export,
    run_analyze_python_metrics,
)


def test_display_format_by_table(capsys, mocker):
    df = pd.DataFrame([{"a": 1, "b": 2}])

    _diplay(df, DisplayFormat.TABLE)
    captured = capsys.readouterr()
    assert "a    b" in captured.out
    assert "1    2" in captured.out


def test_display_format_by_csv(capsys, mocker):
    df = pd.DataFrame([{"a": 1, "b": 2}])
    _diplay(df, DisplayFormat.CSV)
    captured = capsys.readouterr()
    assert "a,b" in captured.out
    assert "1,2" in captured.out


def test_display_format_by_json(capsys, mocker):
    df = pd.DataFrame([{"a": 1, "b": 2}])
    _diplay(df, DisplayFormat.JSON)
    captured = capsys.readouterr()
    assert '[\n  {\n    "a":1,\n    "b":2\n  }\n]\n' in captured.out


def test_export(tmp_path, mocker):
    df = pd.DataFrame([{"a": 1, "b": 2}])
    export_path = tmp_path.joinpath("test.csv")

    assert not export_path.exists()

    _export(df, export_path)
    assert export_path.exists()


def test_export_already_exist_error(tmp_path, mocker):
    df = pd.DataFrame([{"a": 1, "b": 2}])
    export_path = tmp_path.joinpath("test.csv")
    export_path.touch()
    with pytest.raises(FileExistsError):
        _export(df, export_path)


def test_export_already_exist_overwrite(tmp_path, mocker):
    df = pd.DataFrame([{"a": 1, "b": 2}])
    export_path = tmp_path.joinpath("test.csv")
    export_path.touch()

    assert export_path.exists()
    _export(df, export_path, overwrite=True)

    assert export_path.exists()


def test_run_analyze_python_metrics(tmp_path, capsys):
    # テスト用のPythonファイルを作成
    test_file = tmp_path / "test_file.py"

    test_file.write_text("""
def example_function():
    print("Hello, World!")

class ExampleClass:
    def __init__(self):
        self.value = 42

    def example_method(self):
        return self.value
""")

    input_param = InputTargetParameter(path=tmp_path, with_git_repo=False)
    display_param = DisplayParameter(format=DisplayFormat.TABLE)
    export_param = ExportParameter(export_file_path=None)

    # 解析を実行
    run_analyze_python_metrics(input_param, display_param, export_param)

    # 標準出力をキャプチャ
    captured = capsys.readouterr()

    # 期待される出力の検証
    assert "test_file.py" in captured.out
    assert "product" in captured.out  # プロダクトコードとして認識されることを確認

    # メトリクスの存在を確認
    metrics = [
        "lines_of_code",
        "logical_lines_of_code",
        "source_lines_of_code",
        "comments",
        "single_comments",
        "multi",
        "blank",
        "import_count",
        "cyclomatic_complexity",
        "maintainability_index",
        "cognitive_complexity",
    ]
    for metric in metrics:
        assert metric in captured.out

    # 値の存在を確認（厳密な値は環境によって変わる可能性があるため、存在チェックのみ）
    assert any(char.isdigit() for char in captured.out)


def test_run_analyze_python_metrics_with_export(tmp_path):
    # テスト用のPythonファイルを作成
    test_file = tmp_path / "test_file.py"
    test_file.write_text("""
def example_function():
    print("Hello, World!")
""")

    export_file = tmp_path / "output.csv"

    input_param = InputTargetParameter(path=tmp_path, with_git_repo=False)
    display_param = DisplayParameter(format=DisplayFormat.CSV)
    export_param = ExportParameter(export_file_path=export_file)

    # 解析を実行
    run_analyze_python_metrics(input_param, display_param, export_param)

    # エクスポートファイルの存在を確認
    assert export_file.exists()

    # エクスポートされたCSVの内容を確認
    df = pd.read_csv(export_file)
    assert "filepath" in df.columns
    assert "product_or_test" in df.columns
    assert len(df) == 1  # 1つのファイルのみ解析されたことを確認
    assert Path(df.iloc[0]["filepath"]).name == "test_file.py"
    assert df.iloc[0]["product_or_test"] == "product"