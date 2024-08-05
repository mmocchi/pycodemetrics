import logging
import os
from enum import Enum
from pathlib import Path

import pandas as pd
import tabulate
from pycodemetrics.services.analyze_changelogs import (
    FileHotspotMetrics,
    analyze_changelogs_file,
)
from pycodemetrics.util.file_util import (
    get_target_files_by_git_ls_files,
)
from pydantic import BaseModel
from tqdm import tqdm

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


class DisplayParameter(BaseModel, frozen=True):
    format: DisplayFormat = DisplayFormat.TABLE


class ExportParameter(BaseModel, frozen=True):
    export_file_path: Path | None = None
    overwrite: bool = False

    def with_export(self):
        return self.export_file_path is not None


def _diplay(results_df: pd.DataFrame, display_format: DisplayFormat) -> None:
    if display_format == DisplayFormat.TABLE:
        result_table = tabulate.tabulate(results_df, headers="keys")  # type: ignore
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


def _analyze_hotspot_metrics(
    target_file_full_paths: list[Path],
) -> list[FileHotspotMetrics]:
    results = []

    # TODO: filter supported files

    for target_file_full_path in tqdm(target_file_full_paths):
        result = analyze_changelogs_file(target_file_full_path)
        results.append(result)
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
    display_param: DisplayParameter,
    export_param: ExportParameter,
) -> None:
    base_path = None

    target_file_paths = get_target_files_by_git_ls_files(input_param.path)
    base_path = input_param.path

    if len(target_file_paths) == 0:
        logger.warning("No python files found in the specified path.")
        return

    target_file_full_paths = [base_path.joinpath(f) for f in target_file_paths]

    results = _analyze_hotspot_metrics(target_file_full_paths)

    results_df = _transform_for_display(results)

    results_df["filepath"] = results_df["filepath"].map(
        lambda x: os.path.relpath(x, base_path)
    )

    if export_param.with_export():
        _export(results_df, export_param.export_file_path, export_param.overwrite)

    _diplay(results_df, display_param.format)
