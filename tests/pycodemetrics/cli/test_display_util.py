import pandas as pd

from pycodemetrics.cli.display_util import DisplayFormat, display


def test_display_format_by_table(capsys, mocker):
    df = pd.DataFrame([{"a": 1, "b": 2}])

    display(df, DisplayFormat.TABLE)
    captured = capsys.readouterr()
    assert "a    b" in captured.out
    assert "1    2" in captured.out


def test_display_format_by_csv(capsys, mocker):
    df = pd.DataFrame([{"a": 1, "b": 2}])
    display(df, DisplayFormat.CSV)
    captured = capsys.readouterr()
    assert "a,b" in captured.out
    assert "1,2" in captured.out


def test_display_format_by_json(capsys, mocker):
    df = pd.DataFrame([{"a": 1, "b": 2}])
    display(df, DisplayFormat.JSON)
    captured = capsys.readouterr()
    assert '[\n  {\n    "a":1,\n    "b":2\n  }\n]\n' in captured.out
