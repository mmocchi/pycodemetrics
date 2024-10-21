import logging
import os
from enum import Enum
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field, field_validator
from tqdm import tqdm

from pycodemetrics.cli.display_util import DisplayFormat, display, head_for_display
from pycodemetrics.cli.exporter import export
from pycodemetrics.config.config_manager import ConfigManager
from pycodemetrics.services.analyze_python_metrics import (
    AnalyzePythonSettings,
    FilterCodeType,
    PythonFileMetrics,
    analyze_python_file,
)
from pycodemetrics.util.file_util import (
    get_target_files_by_git_ls_files,
    get_target_files_by_path,
)

logger = logging.getLogger(__name__)

Column = Enum(  # type: ignore[misc]
    "Column",
    ((value, value) for value in PythonFileMetrics.get_keys()),
    type=str,
)


class InputTargetParameter(BaseModel, frozen=True, extra="forbid"):
    """
    Input parameters for the target python file or directory.

    path (Path): Path to the target python file or directory.
    with_git_repo (bool): Analyze python files in the git.
    config_file_path (Path): Path to the configuration file.
    """

    path: Path
    with_git_repo: bool
    config_file_path: Path = Path("./pyproject.toml")


class RuntimeParameter(BaseModel, frozen=True, extra="forbid"):
    """
    Runtime parameter for analyze_hotspot_metrics

    Args:
        workers (int | None): Number of workers for multiprocessing. If None, use the number of CPUs.
        filter_code_type (FilterCodeType): Filter code type.
    """

    workers: int | None = Field(default_factory=lambda: os.cpu_count())
    filter_code_type: FilterCodeType = FilterCodeType.PRODUCT


class DisplayParameter(BaseModel, frozen=True, extra="forbid"):
    """
    Display parameters for the result.

    format (DisplayFormat): Display format for the result.
    """

    format: DisplayFormat = DisplayFormat.TABLE
    filter_code_type: FilterCodeType = FilterCodeType.PRODUCT
    limit: int | None = 10
    sort_column: Column = Column.filepath  # type: ignore
    sort_desc: bool = True
    columns: list[Column] | None = Field(
        default_factory=lambda: [Column(k) for k in PythonFileMetrics.get_keys()]
    )

    @field_validator("sort_column")
    def set_sort_column(cls, value: str):
        if value not in PythonFileMetrics.get_keys():
            raise ValueError(f"Invalid sort column: {value}")
        return value

    @field_validator("limit")
    def set_limit(cls, value: int | None):
        if value is None or value <= 0:
            return None
        return value


class ExportParameter(BaseModel, frozen=True, extra="forbid"):
    """
    Export parameters for the result.

    export_file_path (Path): Path to the export file.
    overwrite (bool): Overwrite the export file if it already exists.
    """

    export_file_path: Path | None = None
    overwrite: bool = False

    def with_export(self) -> bool:
        """
        Returns:
            bool: エクスポートするかどうか
        """
        return self.export_file_path is not None


def _analyze_python_metrics(
    target_file_paths: list[Path], settings: AnalyzePythonSettings
) -> list[PythonFileMetrics]:
    results = []
    for filepath in tqdm(target_file_paths):
        if not filepath.suffix == ".py":
            logger.warning(f"Skipping {filepath} as it is not a python file")
            continue

        try:
            result = analyze_python_file(filepath, settings)
            results.append(result)
        except Exception as e:
            logger.warning(f"Skipping {filepath}. cause of error: {e}")
            continue
    return results


def _transform_for_display(results: list[PythonFileMetrics]) -> pd.DataFrame:
    results_flat = [result.to_flat() for result in results]
    return pd.DataFrame(results_flat, columns=list(results_flat[0].keys()))


def _filter_for_display_by_code_type(
    results_df: pd.DataFrame, filter_code_type: FilterCodeType
) -> pd.DataFrame:
    """
    Filter the result of analyze_hotspot_metrics for display by code type

    Args:
        results_df (pd.DataFrame): Result of analyze_hotspot_metrics.
        filter_code_type (FilterCodeType): Filter code type.

    Returns:
        pd.DataFrame: Filtered result for display.
    """
    if filter_code_type == FilterCodeType.BOTH:
        return results_df

    return results_df[results_df["code_type"] == filter_code_type.value]


def _sort_value_for_display(
    results_df: pd.DataFrame, sort_column: Column, sort_desc: bool
) -> pd.DataFrame:
    """
    Sort the result of analyze_hotspot_metrics for display

    Args:
        results_df (pd.DataFrame): Result of analyze_hotspot_metrics.
        sort_column (Column): Column to sort the result.
        sort_desc (bool): Sort the result in descending order.

    Returns:
        pd.DataFrame: Sorted result for display.
    """

    sorted_df = results_df.sort_values(sort_column.value, ascending=not sort_desc)
    return sorted_df.reset_index(drop=True)


def _select_columns_for_display(
    results_df: pd.DataFrame, columns: list[Column] | None
) -> pd.DataFrame:
    """
    Select columns to display from the result of analyze_hotspot_metrics

    Args:
        results_df (pd.DataFrame): Result of analyze_hotspot_metrics.
        columns (list[Columns] | None): Columns to display. If None, display all columns.

    Returns:
        pd.DataFrame: Selected columns for display.
    """
    if columns is None:
        return results_df
    columns = [col.value for col in columns]
    return results_df[columns]


def run_analyze_python_metrics(
    input_param: InputTargetParameter,
    display_param: DisplayParameter,
    export_param: ExportParameter,
) -> None:
    """
    Run the analyze python metrics.

    Args:
        input_param (InputTargetParameter): The input parameters.
        display_param (DisplayParameter): The display parameters.
        export_param (ExportParameter): The export parameters.
    """

    # パラメータの解釈
    base_path = None
    if input_param.with_git_repo:
        target_file_paths = get_target_files_by_git_ls_files(input_param.path)
        base_path = input_param.path
    else:
        target_file_paths = get_target_files_by_path(input_param.path)
        target_file_full_paths = [f for f in target_file_paths]

    if len(target_file_paths) == 0:
        logger.warning("No python files found in the specified path.")
        return

    if base_path is None:
        target_file_full_paths = [f for f in target_file_paths]
    else:
        target_file_full_paths = [base_path.joinpath(f) for f in target_file_paths]

    config_file_path = input_param.config_file_path
    analyze_settings = AnalyzePythonSettings(
        testcode_type_patterns=ConfigManager.get_testcode_type_patterns(
            config_file_path
        ),
        user_groups=ConfigManager.get_user_groups(config_file_path),
    )

    # メイン処理の実行
    results = _analyze_python_metrics(target_file_full_paths, analyze_settings)

    # 結果の整形
    results_df = _transform_for_display(results)
    if len(results) == 0:
        logger.warning("No results found.")
        return

    if base_path is None:
        pass
    else:
        results_df["filepath"] = results_df["filepath"].map(
            lambda x: os.path.relpath(x, base_path)
        )

    # 結果の表示
    display_df = results_df.copy()
    display_df = _filter_for_display_by_code_type(
        display_df, display_param.filter_code_type
    )
    display_df = _sort_value_for_display(
        display_df, display_param.sort_column, display_param.sort_desc
    )
    display_df = _select_columns_for_display(display_df, display_param.columns)
    display_df = head_for_display(display_df, display_param.limit)

    if export_param.with_export():
        export(results_df, export_param.export_file_path, export_param.overwrite)

    display(display_df, display_param.format)
