import pandas as pd
import pytest

from pycodemetrics.cli.exporter import export


def test_export(tmp_path, mocker):
    df = pd.DataFrame([{"a": 1, "b": 2}])
    export_path = tmp_path.joinpath("test.csv")

    assert not export_path.exists()

    export(df, export_path)
    assert export_path.exists()


def test_export_already_exist_error(tmp_path, mocker):
    df = pd.DataFrame([{"a": 1, "b": 2}])
    export_path = tmp_path.joinpath("test.csv")
    export_path.touch()
    with pytest.raises(FileExistsError):
        export(df, export_path)


def test_export_already_exist_overwrite(tmp_path, mocker):
    df = pd.DataFrame([{"a": 1, "b": 2}])
    export_path = tmp_path.joinpath("test.csv")
    export_path.touch()

    assert export_path.exists()
    export(df, export_path, overwrite=True)

    assert export_path.exists()
