import datetime as dt
import logging
import os
from concurrent.futures import as_completed
from concurrent.futures.process import ProcessPoolExecutor
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import pandas as pd
import tabulate
from pydantic import BaseModel, validator
from tqdm import tqdm

from pycodemetrics.config.config_manager import ConfigManager
from pycodemetrics.services.analyze_changelogs import (
    AnalizeChangeLogSettings,
    FileHotspotMetrics,
    analyze_changelogs_file,
)
from pycodemetrics.util.file_util import (
    get_target_files_by_git_ls_files,
)

logger = logging.getLogger(__name__)


class DisplayFormat(str, Enum):
    TABLE = "table"
    CSV = "csv"
    JSON = "json"

    @classmethod
    def to_list(cls):
        return [e.value for e in cls]


class ExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"

    @classmethod
    def to_list(cls):
        return [e.value for e in cls]

    def get_ext(self):
        return f".{self.value}"


class InputTargetParameter(BaseModel, frozen=True):
    path: Path
    config_file_path: Path = Path("./pyproject.toml")


class RuntimeParameter(BaseModel, frozen=True):
    workers: int

    @validator("workers", pre=True)
    def set_workers(cls, value: int):
        if value is None or value <= 0:
            return os.cpu_count()
        return value


class DisplayParameter(BaseModel, frozen=True):
    format: DisplayFormat = DisplayFormat.TABLE


class ExportParameter(BaseModel, frozen=True):
    export_file_path: Path | None = None
    overwrite: bool = False

    def with_export(self):
        return self.export_file_path is not None


def _diplay(results_df: pd.DataFrame, display_format: DisplayFormat) -> None:
    if display_format == DisplayFormat.TABLE:
        result_table = tabulate.tabulate(results_df, headers="keys", floatfmt=".6f")  # type: ignore
        print(result_table)
    elif display_format == DisplayFormat.CSV:
        print(results_df.to_csv(index=False))
    elif display_format == DisplayFormat.JSON:
        print(
            results_df.to_json(
                orient="records", indent=2, force_ascii=False, default_handler=str
            )
        )
    else:
        raise ValueError(f"Invalid display format: {display_format}")


@dataclass
class InputTarget:
    target_file_full_path: Path
    git_repo_path: Path


def _analyze_hotspot_metrics_file(
    target_file_path, git_repo_path, settings
) -> FileHotspotMetrics:
    return analyze_changelogs_file(target_file_path, git_repo_path, settings)


def _analyze_hotspot_metrics(
    target_file_paths: list[Path],
    git_repo_path: Path,
    settings: AnalizeChangeLogSettings,
) -> list[FileHotspotMetrics]:
    results = []

    for target in tqdm(target_file_paths):
        try:
            print(target)
            result = _analyze_hotspot_metrics_file(target, git_repo_path, settings)
            print(result)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to analyze {target}: {e}")
            continue
    return results


def _analyze_hotspot_metrics_for_multiprocessing(
    target_file_paths: list[Path],
    git_repo_path: Path,
    settings: AnalizeChangeLogSettings,
    workers: int = 16,
) -> list[FileHotspotMetrics]:
    results = []

    # TODO: filter supported files

    results = []
    with tqdm(total=len(target_file_paths)) as pbar:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    _analyze_hotspot_metrics_file, target, git_repo_path, settings
                )
                for target in target_file_paths
            }

            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    logger.error(f"Failed to analyze {future.exception}: {e}")
                    continue
                pbar.update(1)

    return results


def _transform_for_display(results: list[FileHotspotMetrics]) -> pd.DataFrame:
    results_flat = [result.to_flat() for result in results]
    return pd.DataFrame(results_flat, columns=results_flat[0].keys())


def _export(
    results_df: pd.DataFrame,
    export_file_path: Path | None,
    overwrite: bool = False,
) -> None:
    if export_file_path is None:
        raise ValueError("Export file path is not specified")

    if export_file_path.exists() and not overwrite:
        raise FileExistsError(
            f"{export_file_path} already exists. Use --overwrite option to overwrite the file"
        )

    export_file_path.parent.mkdir(parents=True, exist_ok=True)

    if export_file_path.suffix == ExportFormat.CSV.get_ext():
        results_df.to_csv(export_file_path, index=False)
    elif export_file_path.suffix == ExportFormat.JSON.get_ext():
        results_df.to_json(
            export_file_path, orient="records", indent=4, force_ascii=False
        )
    else:
        raise ValueError(f"Invalid export format: {export_file_path.suffix}")


def run_analyze_hotspot_metrics(
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
    settings = AnalizeChangeLogSettings(
        base_datetime=dt.datetime.now(dt.timezone.utc).astimezone(),
        testcode_type_patterns=ConfigManager.get_testcode_type_patterns(
            config_file_path
        ),
        user_groups=ConfigManager.get_user_groups(config_file_path),
    )

    if runtime_param.workers <= 1:
        results = _analyze_hotspot_metrics(
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
    results_df = results_df.sort_values("hotspot", ascending=False)

    if export_param.with_export():
        _export(results_df, export_param.export_file_path, export_param.overwrite)

    _diplay(results_df, display_param.format)
