import datetime as dt
import logging
import os
from enum import Enum
from pathlib import Path

import pandas as pd
import tabulate
from pydantic import BaseModel
from tqdm import tqdm

from pycodemetrics.services.analyze_python_metrics import (
    PythonFileMetrics,
    analyze_python_file,
)
from pycodemetrics.util.file_util import (
    get_target_files_by_git_ls_files,
    get_target_files_by_path,
)

logger = logging.getLogger(__name__)


class DisplayFormat(str, Enum):
    TABLE = "table"
    CSV = "csv"
    JSON = "json"


class ExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"


class InputTargetParameter(BaseModel, frozen=True):
    path: Path
    with_git_repo: bool


class DisplayParameter(BaseModel, frozen=True):
    format: DisplayFormat = DisplayFormat.TABLE


class ExportParameter(BaseModel, frozen=True):
    export_format: ExportFormat = ExportFormat.CSV
    export_file_path: Path | None = None
    overwrite: bool = False

    def get_export_file_path(self) -> Path:
        if self.export_file_path is None:
            return self._create_default_export_file_path()
        return self.export_file_path

    def _create_default_export_file_path(self) -> Path:
        now = dt.datetime.now().strftime("%Y%m%d%H%M%S")
        return Path(f"./pycondmetrics_analyze_{now}.{self.export_format}")


def _diplay(results_df: pd.DataFrame, display_format: DisplayFormat) -> None:
    if display_format == DisplayFormat.TABLE:
        result_table = tabulate.tabulate(results_df, headers="keys")  # type: ignore
        print(result_table)
    elif display_format == DisplayFormat.CSV:
        print(results_df.to_csv(index=False))
    elif display_format == DisplayFormat.JSON:
        print(results_df.to_json(orient="records"))
    else:
        raise ValueError(f"Invalid display format: {display_format}")


def _export(
    results_df: pd.DataFrame,
    export_format: ExportFormat,
    export_file_path: Path,
    overwrite: bool = False,
) -> None:
    if export_file_path.exists() and not overwrite:
        raise FileExistsError(
            f"{export_file_path} already exists. Use --overwrite option to overwrite the file"
        )
    if export_format == ExportFormat.CSV:
        results_df.to_csv(export_file_path, index=False)
    elif export_format == ExportFormat.JSON:
        results_df.to_json(export_file_path, orient="records")
    else:
        raise ValueError(f"Invalid export format: {export_format}")


def _analyze_python_metrics(target_file_paths: list[str]) -> list[PythonFileMetrics]:
    results = []
    for filepath in tqdm(target_file_paths):
        if not filepath.endswith(".py"):
            logger.warning(f"Skipping {filepath} as it is not a python file")
            continue

        try:
            result = analyze_python_file(filepath)
            results.append(result)
        except Exception as e:
            logger.warning(f"Skipping {filepath}. cause of error: {e}")
            continue
    return results


def _transform_for_display(results: list[PythonFileMetrics]) -> pd.DataFrame:
    results_flat = [result.to_flat() for result in results]
    return pd.DataFrame(results_flat, columns=results_flat[0].keys())


def run_analyze_python_metrics(input_param: InputTargetParameter) -> None:
    if input_param.with_git_repo:
        target_file_paths = get_target_files_by_git_ls_files(input_param.path)
        base_path = input_param.path
    else:
        target_file_paths = get_target_files_by_path(input_param.path)
        base_path = Path.cwd()

    if len(target_file_paths) == 0:
        logger.warning("No python files found in the specified path.")
        return

    target_file_full_paths = [os.path.join(base_path, f) for f in target_file_paths]
    results = _analyze_python_metrics(target_file_full_paths)

    results_df = _transform_for_display(results)
    results_df["filepath"] = results_df["filepath"].map(
        lambda x: os.path.relpath(x, base_path)
    )
    result_table = tabulate.tabulate(results_df, headers="keys")  # type: ignore
    print(result_table)
