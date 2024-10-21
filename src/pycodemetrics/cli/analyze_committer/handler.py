import datetime as dt
import logging
import os
from concurrent.futures import as_completed
from concurrent.futures.process import ProcessPoolExecutor
from enum import Enum
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field, field_validator
from tqdm import tqdm

from pycodemetrics.cli.display_util import DisplayFormat, display, head_for_display
from pycodemetrics.cli.exporter import export
from pycodemetrics.config.config_manager import ConfigManager
from pycodemetrics.services.analyze_committer import (
    AnalizeCommitterSettings,
    FileChangeCountMetrics,
    FilterCodeType,
    aggregate_changecount_by_committer,
)
from pycodemetrics.util.file_util import (
    get_code_type,
    get_target_files_by_git_ls_files,
)

logger = logging.getLogger(__name__)


class DisplayColumn(str, Enum):
    COMMITTER = "committer"
    CHANGE_COUNT = "change_count"

    @classmethod
    def keys(cls) -> list["DisplayColumn"]:
        return [e for e in cls]

    @classmethod
    def to_list(cls) -> list[str]:
        return [e.value for e in cls]


class InputTargetParameter(BaseModel, frozen=True, extra="forbid"):
    """
    Input parameter for analyze_hotspot_metrics

    Args:
        path (Path): Path to the target directory of git repository.
        config_file_path (Path): Path to the configuration file.
    """

    path: Path
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
    Display parameter for analyze_hotspot_metrics

    Args:
        format (DisplayFormat): Display format.
        filter_code_type (FilterCodeType): Filter code type.
        limit (int | None): Limit the number of files to display. If None, display all files.
        sort_column (str): Column to sort the result.
        sort_desc (bool): Sort the result in descending order.
        columns (list[Columns] | None): Columns to display. If None, display all columns.
    """

    format: DisplayFormat = DisplayFormat.TABLE
    filter_code_type: FilterCodeType = FilterCodeType.PRODUCT
    limit: int | None = 10
    sort_column: DisplayColumn = DisplayColumn.CHANGE_COUNT  # type: ignore
    sort_desc: bool = True
    columns: list[DisplayColumn] | None = Field(
        default_factory=lambda: DisplayColumn.keys()
    )

    @field_validator("sort_column")
    def set_sort_column(cls, value: str):
        if value not in DisplayColumn.to_list():
            raise ValueError(f"Invalid sort column: {value}")
        return value

    @field_validator("limit")
    def set_limit(cls, value: int | None):
        if value is None or value <= 0:
            return None
        return value


class ExportParameter(BaseModel, frozen=True, extra="forbid"):
    """
    Export parameter for analyze_hotspot_metrics

    Args:
        export_file_path (Path | None): Export file path. If None, export is not executed.
        overwrite (bool): Overwrite the export file if it already exists.
    """

    export_file_path: Path | None = None
    overwrite: bool = False

    def with_export(self) -> bool:
        """
        Returns:
            bool: エクスポートを実行するかどうか
        """
        return self.export_file_path is not None


def _filter_target_by_code_type(
    target_file_paths: list[Path], settings: AnalizeCommitterSettings
) -> list[Path]:
    if settings.filter_code_type == FilterCodeType.BOTH:
        return target_file_paths

    return [
        target
        for target in target_file_paths
        if get_code_type(target, settings.testcode_type_patterns).value
        == settings.filter_code_type.value
    ]


def _analyze_committer_metrics(
    target_file_paths: list[Path],
    git_repo_path: Path,
    settings: AnalizeCommitterSettings,
) -> list[FileChangeCountMetrics]:
    results: list[FileChangeCountMetrics] = []

    target_file_paths_ = _filter_target_by_code_type(target_file_paths, settings)

    for target in tqdm(target_file_paths_):
        try:
            result = aggregate_changecount_by_committer(target, git_repo_path, settings)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to analyze {target}: {e}")
            continue
    return results


def _analyze_hotspot_metrics_for_multiprocessing(
    target_file_paths: list[Path],
    git_repo_path: Path,
    settings: AnalizeCommitterSettings,
    workers: int = 16,
) -> list[FileChangeCountMetrics]:
    target_file_paths_ = _filter_target_by_code_type(target_file_paths, settings)

    results: list[FileChangeCountMetrics] = []
    with tqdm(total=len(target_file_paths_)) as pbar:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    aggregate_changecount_by_committer, target, git_repo_path, settings
                )
                for target in target_file_paths_
            }

            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    logger.error(f"Failed to analyze {future.exception}: {e}")
                    continue
                pbar.update(1)

    return results


def _transform_for_display(results: list[FileChangeCountMetrics]) -> pd.DataFrame:
    """
    Transform the result of analyze_committer_metrics for display

    Args:
        results (list[FileChangeCountMetrics]): Result of analyze_committer_metrics.

    Returns:
        pd.DataFrame: Transformed result for display.
    """
    results_flat: list[dict[str, Any]] = []
    for result in results:
        results_flat = results_flat + result.to_flatten_list()
    flat_df = pd.DataFrame(results_flat, columns=list(results_flat[0].keys()))

    # aggreage by committer
    results_df = (
        flat_df[["committer", "change_count"]]
        .groupby(["committer"])
        .sum()
        .reset_index()
    )
    return results_df


def _filter_for_display_by_code_type(
    results_df: pd.DataFrame, filter_code_type: FilterCodeType
) -> pd.DataFrame:
    """
    Filter the result of analyze_committer_metrics for display by code type

    Args:
        results_df (pd.DataFrame): Result of analyze_committer_metrics.
        filter_code_type (FilterCodeType): Filter code type.

    Returns:
        pd.DataFrame: Filtered result for display.
    """
    if filter_code_type == FilterCodeType.BOTH:
        return results_df

    return results_df[results_df["code_type"] == filter_code_type.value]


def _sort_value_for_display(
    results_df: pd.DataFrame, sort_column: DisplayColumn, sort_desc: bool
) -> pd.DataFrame:
    """
    Sort the result of analyze_committer_metrics for display

    Args:
        results_df (pd.DataFrame): Result of analyze_committer_metrics.
        sort_column (Column): Column to sort the result.
        sort_desc (bool): Sort the result in descending order.

    Returns:
        pd.DataFrame: Sorted result for display.
    """

    sorted_df = results_df.sort_values(sort_column.value, ascending=not sort_desc)
    return sorted_df.reset_index(drop=True)


def _select_columns_for_display(
    results_df: pd.DataFrame, columns: list[DisplayColumn] | None
) -> pd.DataFrame:
    """
    Select columns to display from the result of analyze_committer_metrics

    Args:
        results_df (pd.DataFrame): Result of analyze_committer_metrics.
        columns (list[DisplayColumn] | None): Columns to display. If None, display all columns.

    Returns:
        pd.DataFrame: Selected columns for display.
    """
    if columns is None:
        return results_df
    selected_columns = [col.value for col in columns]
    return results_df[selected_columns]


def run_analyze_committer_metrics(
    input_param: InputTargetParameter,
    runtime_param: RuntimeParameter,
    display_param: DisplayParameter,
    export_param: ExportParameter,
) -> None:
    # パラメータの処理
    target_file_paths = get_target_files_by_git_ls_files(input_param.path)

    if len(target_file_paths) == 0:
        logger.warning("No python files found in the specified path.")
        return

    # 解析の実行
    config_file_path = input_param.config_file_path
    settings = AnalizeCommitterSettings(
        base_datetime=dt.datetime.now(dt.timezone.utc).astimezone(),
        testcode_type_patterns=ConfigManager.get_testcode_type_patterns(
            config_file_path
        ),
        user_groups=ConfigManager.get_user_groups(config_file_path),
        filter_code_type=runtime_param.filter_code_type,
    )

    workers = runtime_param.workers or os.cpu_count()
    if workers is None:
        raise ValueError("Invalid workers: None")

    if workers <= 1:
        results = _analyze_committer_metrics(
            target_file_paths, input_param.path, settings
        )
    else:
        results = _analyze_hotspot_metrics_for_multiprocessing(
            target_file_paths, input_param.path, settings
        )

    if len(results) == 0:
        logger.warning("No results found.")
        return

    # 結果の表示
    results_df = _transform_for_display(results)

    display_df = results_df.copy()
    display_df = _sort_value_for_display(
        display_df, display_param.sort_column, display_param.sort_desc
    )
    display_df = _select_columns_for_display(display_df, display_param.columns)
    display_df = head_for_display(display_df, display_param.limit)

    if export_param.with_export():
        export(results_df, export_param.export_file_path, export_param.overwrite)

    display(display_df, display_param.format)
