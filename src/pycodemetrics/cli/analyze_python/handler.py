"""Pythonコード分析ハンドラーモジュール。

このモジュールは、Pythonコードのメトリクス分析を行うためのハンドラーを提供します。
分析対象のファイルの取得、分析の実行、結果の表示・エクスポートなどの機能を提供します。

主な機能:
    - 分析対象ファイルの取得と検証
    - コードメトリクスの計算と分析
    - 結果の表示形式の制御
    - 分析結果のエクスポート

処理フロー:
    1. 入力パラメータの検証
    2. 分析対象ファイルの取得
    3. コードメトリクスの計算
    4. 結果のフィルタリングとソート
    5. 結果の表示とエクスポート

制限事項:
    - 分析対象はPythonファイルのみ
    - ファイルサイズの制限あり
    - エンコーディングはUTF-8のみ対応
"""

import logging
import os
from concurrent.futures import as_completed
from concurrent.futures.process import ProcessPoolExecutor
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
    get_code_type,
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
    """入力パラメータクラス。

    分析対象のPythonファイルまたはディレクトリに関するパラメータを定義します。

    Attributes:
        path (Path): 分析対象のPythonファイルまたはディレクトリのパス
        with_git_repo (bool): Gitリポジトリ内のPythonファイルを分析するかどうか。Falseの場合は指定されたパス内を再帰的に探索する
        config_file_path (Path): 設定ファイルのパス
    """

    path: Path
    with_git_repo: bool
    config_file_path: Path = Path("./pyproject.toml")


class RuntimeParameter(BaseModel, frozen=True, extra="forbid"):
    """実行時パラメータクラス。

    分析の実行に関するパラメータを定義します。

    Attributes:
        workers (int | None): マルチプロセッシングのワーカー数。Noneの場合はCPU数を使用
        filter_code_type (FilterCodeType): フィルタリングするコードタイプ
    """

    workers: int | None = Field(default_factory=lambda: os.cpu_count())
    filter_code_type: FilterCodeType = FilterCodeType.PRODUCT


class DisplayParameter(BaseModel, frozen=True, extra="forbid"):
    """表示パラメータクラス。

    分析結果の表示に関するパラメータを定義します。

    Attributes:
        format (DisplayFormat): 表示フォーマット
        filter_code_type (FilterCodeType): フィルタリングするコードタイプ
        limit (int | None): 表示する行数の制限
        sort_column (Column): ソート対象のカラム
        sort_desc (bool): 降順でソートするかどうか
        columns (list[Column] | None): 表示するカラムのリスト
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
    def set_sort_column(cls, value: str) -> str:
        """sort_columnのバリデーション。

        Args:
            value (str): 検証するソートカラム

        Returns:
            str: 検証済みのソートカラム

        Raises:
            ValueError: 無効なソートカラムが指定された場合
        """
        if value not in PythonFileMetrics.get_keys():
            raise ValueError(f"Invalid sort column: {value}")
        return value

    @field_validator("limit")
    def set_limit(cls, value: int | None) -> int | None:
        """表示行数制限のバリデーション。

        Args:
            value (int | None): 検証する表示行数制限

        Returns:
            int | None: 検証済みの表示行数制限
        """
        if value is None or value <= 0:
            return None
        return value


class ExportParameter(BaseModel, frozen=True, extra="forbid"):
    """エクスポート用のパラメータクラス。

    分析結果のエクスポートに関するパラメータを定義します。

    Attributes:
        export_file_path (Path | None): エクスポート先のファイルパス
        overwrite (bool): 既存のファイルを上書きするかどうか
    """

    export_file_path: Path | None = None
    overwrite: bool = False

    def with_export(self) -> bool:
        """エクスポートを行うかどうかを判定します。

        Returns:
            bool: エクスポートを行う場合はTrue、そうでない場合はFalse
        """
        return self.export_file_path is not None


def _filter_target_by_code_type(
    target_file_paths: list[Path], settings: AnalyzePythonSettings
) -> list[Path]:
    if settings.filter_code_type == FilterCodeType.BOTH:
        return target_file_paths

    return [
        target
        for target in target_file_paths
        if get_code_type(target, settings.testcode_type_patterns).value
        == settings.filter_code_type.value
    ]


def _analyze_python_metrics(
    target_file_paths: list[Path], settings: AnalyzePythonSettings
) -> list[PythonFileMetrics]:
    """Pythonファイルのメトリクスを分析します。

    Args:
        target_file_paths (list[Path]): 分析対象のファイルパスのリスト
        settings (AnalyzePythonSettings): 分析設定

    Returns:
        list[PythonFileMetrics]: 分析結果となるPythonFileMetricsのリスト
    """
    results = []

    target_file_paths_ = _filter_target_by_code_type(target_file_paths, settings)

    for filepath in tqdm(target_file_paths_):
        if not filepath.suffix == ".py":
            logger.warning(f"Skipping {filepath} as it is not a python file")
            continue

        try:
            result = analyze_python_file(filepath, settings)
            results.append(result)
        except Exception as e:
            logger.warning(
                f"Skipping {filepath} due to error: {type(e).__name__}: {str(e)}"
            )
            continue
    return results


def _transform_for_display(results: list[PythonFileMetrics]) -> pd.DataFrame:
    """分析結果を表示用のDataFrameに変換します。

    Args:
        results (list[PythonFileMetrics]): 分析結果のリスト

    Returns:
        pd.DataFrame: 表示用のDataFrame
    """
    results_flat = [result.to_flat() for result in results]
    return pd.DataFrame(results_flat, columns=list(results_flat[0].keys()))


def _filter_for_display_by_code_type(
    results_df: pd.DataFrame, filter_code_type: FilterCodeType
) -> pd.DataFrame:
    """コードタイプでフィルタリングします。

    Args:
        results_df (pd.DataFrame): 分析結果のDataFrame
        filter_code_type (FilterCodeType): フィルタリングするコードタイプ

    Returns:
        pd.DataFrame: フィルタリング後のDataFrame
    """
    if filter_code_type == FilterCodeType.BOTH:
        return results_df

    return results_df[results_df["code_type"] == filter_code_type.value]


def _sort_value_for_display(
    results_df: pd.DataFrame, sort_column: Column, sort_desc: bool
) -> pd.DataFrame:
    """分析結果をソートします。

    Args:
        results_df (pd.DataFrame): 分析結果のDataFrame
        sort_column (Column): ソート対象のカラム
        sort_desc (bool): 降順でソートするかどうか

    Returns:
        pd.DataFrame: ソート後のDataFrame
    """
    sorted_df = results_df.sort_values(sort_column.value, ascending=not sort_desc)
    return sorted_df.reset_index(drop=True)


def _select_columns_for_display(
    results_df: pd.DataFrame, columns: list[Column] | None
) -> pd.DataFrame:
    """表示するカラムを選択します。

    Args:
        results_df (pd.DataFrame): 分析結果のDataFrame
        columns (list[Column] | None): 表示するカラムのリスト。Noneの場合は全カラムを表示

    Returns:
        pd.DataFrame: 選択されたカラムのDataFrame
    """
    if columns is None:
        return results_df
    columns = [col.value for col in columns]
    return results_df[columns]


def _analyze_python_metrics_for_multiprocessing(
    target_file_paths: list[Path],
    settings: AnalyzePythonSettings,
    workers: int = 16,
) -> list[PythonFileMetrics]:
    """マルチプロセスでPythonファイルのメトリクスを分析します。

    Args:
        target_file_paths (list[Path]): 分析対象のファイルパスのリスト
        settings (AnalyzePythonSettings): 分析設定
        workers (int, optional): ワーカー数. Defaults to 16.

    Returns:
        list[PythonFileMetrics]: 分析結果となるPythonFileMetricsのリスト
    """
    results: list[PythonFileMetrics] = []

    target_file_paths_ = _filter_target_by_code_type(target_file_paths, settings)

    with tqdm(total=len(target_file_paths_)) as pbar:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(analyze_python_file, target, settings)
                for target in target_file_paths
                if target.suffix == ".py"
            }

            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    logger.error(f"Failed to analyze {future.exception}: {e}")
                    continue
                pbar.update(1)

    return results


def run_analyze_python_metrics(
    input_param: InputTargetParameter,
    runtime_param: RuntimeParameter,
    display_param: DisplayParameter,
    export_param: ExportParameter,
) -> None:
    """Pythonコードのメトリクス分析を実行します。

    Args:
        input_param (InputTargetParameter): 入力パラメータ
        runtime_param (RuntimeParameter): 実行時パラメータ
        display_param (DisplayParameter): 表示パラメータ
        export_param (ExportParameter): エクスポートパラメータ

    Returns:
        None
    """
    # パラメータの解釈
    exclude_patterns = ConfigManager.get_exclude_patterns(input_param.config_file_path)
    base_path = None
    if input_param.with_git_repo:
        target_file_paths = get_target_files_by_git_ls_files(
            input_param.path, exclude_patterns
        )
        base_path = input_param.path
    else:
        target_file_paths = get_target_files_by_path(input_param.path, exclude_patterns)
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
        filter_code_type=runtime_param.filter_code_type,
    )

    # メイン処理の実行
    workers = runtime_param.workers or os.cpu_count()
    if workers is None:
        raise ValueError("Invalid workers: None")

    if workers <= 1:
        results = _analyze_python_metrics(target_file_full_paths, analyze_settings)
    else:
        results = _analyze_python_metrics_for_multiprocessing(
            target_file_full_paths, analyze_settings, workers
        )

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

    # 結果の表示
    display(display_df, display_param.format)

    # 結果のエクスポート
    if export_param.with_export():
        export(display_df, export_param.export_file_path, export_param.overwrite)
