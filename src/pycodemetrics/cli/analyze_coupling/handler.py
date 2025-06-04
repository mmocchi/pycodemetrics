"""coupling分析ハンドラーモジュール。

このモジュールは、プロジェクト全体のモジュール結合度分析を行うためのハンドラーを提供します。
プロジェクト構造の分析、結合度メトリクスの計算、結果の表示・エクスポートなどの機能を提供します。

主な機能:
    - プロジェクトルートの検証
    - モジュール結合度の計算と分析
    - 結果のフィルタリングとソート
    - プロジェクトサマリーの生成
    - 結果の表示とエクスポート

処理フロー:
    1. 入力パラメータの検証
    2. プロジェクト全体の結合度分析
    3. 結果のフィルタリングとソート
    4. サマリー情報の生成（オプション）
    5. 結果の表示とエクスポート

制限事項:
    - 分析対象はPythonファイルのみ
    - 動的インポートは検出できません
    - 大規模プロジェクトでは処理時間がかかる場合があります
"""

import logging
from enum import Enum
from pathlib import Path
from typing import List, Optional

import pandas as pd
from pydantic import BaseModel, Field, field_validator

from pycodemetrics.cli.display_util import DisplayFormat, display, head_for_display
from pycodemetrics.cli.exporter import export
from pycodemetrics.metrics.coupling import (
    CouplingMetrics,
    ProjectCouplingMetrics,
    analyze_project_coupling,
)

logger = logging.getLogger(__name__)

# 利用可能な列の定義
AVAILABLE_COLUMNS = [
    "module_path",
    "afferent_coupling",
    "efferent_coupling",
    "instability",
    "lines_of_code",
    "category",
    "distance_from_main_sequence",
]

Column = Enum(  # type: ignore[misc]
    "Column",
    ((value, value) for value in AVAILABLE_COLUMNS),
    type=str,
)


class InputParameter(BaseModel, frozen=True, extra="forbid"):
    """入力パラメータクラス。

    結合度分析の対象プロジェクトに関するパラメータを定義します。

    Attributes:
        project_path (Path): 分析対象のプロジェクトルートディレクトリ
        exclude_patterns (Optional[List[str]]): 除外するパターンのリスト
    """

    project_path: Path
    exclude_patterns: Optional[List[str]] = None

    @field_validator("project_path")
    def validate_project_path(cls, v: Path) -> Path:
        """プロジェクトパスの検証"""
        if not v.exists():
            raise ValueError(f"Project path does not exist: {v}")
        if not v.is_dir():
            raise ValueError(f"Project path is not a directory: {v}")
        return v


class DisplayParameter(BaseModel, frozen=True, extra="forbid"):
    """表示パラメータクラス。

    結合度分析結果の表示に関するパラメータを定義します。

    Attributes:
        format (DisplayFormat): 表示フォーマット
        columns (Optional[List[str]]): 表示するカラムのリスト
        limit (Optional[int]): 表示する行数の制限
        sort_column (str): ソート対象のカラム
        sort_desc (bool): 降順でソートするかどうか
        show_summary (bool): プロジェクトサマリーを表示するかどうか
    """

    format: DisplayFormat = DisplayFormat.TABLE
    columns: Optional[List[str]] = None
    limit: Optional[int] = None
    sort_column: str = "instability"
    sort_desc: bool = True
    show_summary: bool = False

    @field_validator("sort_column")
    def validate_sort_column(cls, v: str) -> str:
        """ソートカラムの検証"""
        if v not in AVAILABLE_COLUMNS:
            raise ValueError(
                f"Invalid sort column: {v}. Available: {AVAILABLE_COLUMNS}"
            )
        return v

    @field_validator("columns")
    def validate_columns(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """表示カラムの検証"""
        if v is None:
            return v
        invalid_columns = [col for col in v if col not in AVAILABLE_COLUMNS]
        if invalid_columns:
            raise ValueError(
                f"Invalid columns: {invalid_columns}. Available: {AVAILABLE_COLUMNS}"
            )
        return v

    @field_validator("limit")
    def validate_limit(cls, v: Optional[int]) -> Optional[int]:
        """表示行数制限の検証"""
        if v is not None and v <= 0:
            return None
        return v


class FilterParameter(BaseModel, frozen=True, extra="forbid"):
    """フィルターパラメータクラス。

    結合度分析結果のフィルタリングに関するパラメータを定義します。

    Attributes:
        filter_type (str): フィルタータイプ
        instability_threshold (float): 不安定度の閾値
        coupling_threshold (int): 結合度の閾値
    """

    filter_type: str = "all"
    instability_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    coupling_threshold: int = Field(default=5, ge=0)

    @field_validator("filter_type")
    def validate_filter_type(cls, v: str) -> str:
        """フィルタータイプの検証"""
        valid_types = ["all", "stable", "unstable", "high-coupling"]
        if v not in valid_types:
            raise ValueError(f"Invalid filter type: {v}. Available: {valid_types}")
        return v


class ExportParameter(BaseModel, frozen=True, extra="forbid"):
    """エクスポート用のパラメータクラス。

    結合度分析結果のエクスポートに関するパラメータを定義します。

    Attributes:
        export_file_path (Optional[Path]): エクスポート先のファイルパス
        overwrite (bool): 既存のファイルを上書きするかどうか
    """

    export_file_path: Optional[Path] = None
    overwrite: bool = False

    def with_export(self) -> bool:
        """エクスポートを行うかどうかを判定します。

        Returns:
            bool: エクスポートを行う場合はTrue、そうでない場合はFalse
        """
        return self.export_file_path is not None


def _filter_modules(
    modules: List[CouplingMetrics], filter_param: FilterParameter
) -> List[CouplingMetrics]:
    """モジュールリストをフィルタリング"""
    if filter_param.filter_type == "all":
        return modules
    elif filter_param.filter_type == "stable":
        return [
            m
            for m in modules
            if m.instability < (1 - filter_param.instability_threshold)
        ]
    elif filter_param.filter_type == "unstable":
        return [
            m for m in modules if m.instability > filter_param.instability_threshold
        ]
    elif filter_param.filter_type == "high-coupling":
        return [
            m
            for m in modules
            if m.afferent_coupling > filter_param.coupling_threshold
            or m.efferent_coupling > filter_param.coupling_threshold
        ]
    else:
        return modules


def _transform_for_display(
    modules: List[CouplingMetrics], columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """モジュールリストを表示用のDataFrameに変換"""
    if not modules:
        return pd.DataFrame()

    # データを辞書形式に変換
    data = []
    for module in modules:
        row = {
            "module_path": module.module_path,
            "afferent_coupling": module.afferent_coupling,
            "efferent_coupling": module.efferent_coupling,
            "instability": round(module.instability, 3),
            "lines_of_code": module.lines_of_code,
            "category": module.category,
            "distance_from_main_sequence": round(module.distance_from_main_sequence, 3),
        }
        data.append(row)

    df = pd.DataFrame(data)

    # 指定された列のみを選択
    if columns:
        available_cols = [col for col in columns if col in df.columns]
        df = df[available_cols]

    return df


def _sort_dataframe(
    df: pd.DataFrame, sort_column: str, sort_desc: bool
) -> pd.DataFrame:
    """DataFrameをソート"""
    if sort_column in df.columns:
        df = df.sort_values(sort_column, ascending=not sort_desc)
        return df.reset_index(drop=True)
    return df


def _create_summary_display(project_metrics: ProjectCouplingMetrics) -> pd.DataFrame:
    """プロジェクトサマリーの表示用DataFrameを作成"""
    summary_data = {
        "メトリクス": [
            "総モジュール数",
            "総内部依存関係数",
            "依存関係密度",
            "平均不安定度",
            "最大入力結合度",
            "最大出力結合度",
            "不安定モジュール数 (I>0.8)",
            "安定モジュール数 (I<0.2)",
            "高結合モジュール数 (Ca>5 or Ce>5)",
        ],
        "値": [
            project_metrics.module_count,
            project_metrics.total_internal_dependencies,
            round(project_metrics.dependency_density, 3),
            round(project_metrics.average_instability, 3),
            project_metrics.max_afferent_coupling,
            project_metrics.max_efferent_coupling,
            len(project_metrics.get_unstable_modules(0.8)),
            len(project_metrics.get_stable_modules(0.2)),
            len(project_metrics.get_high_coupling_modules(5, 5)),
        ],
    }
    return pd.DataFrame(summary_data)


def run_analyze_coupling(
    input_param: InputParameter,
    display_param: DisplayParameter,
    filter_param: FilterParameter,
    export_param: ExportParameter,
) -> None:
    """モジュール結合度分析を実行

    Args:
        input_param (InputParameter): 入力パラメータ
        display_param (DisplayParameter): 表示パラメータ
        filter_param (FilterParameter): フィルターパラメータ
        export_param (ExportParameter): エクスポートパラメータ

    Returns:
        None
    """
    # プロジェクト全体の結合度分析を実行
    logger.info(f"Analyzing coupling for project: {input_param.project_path}")

    try:
        project_metrics = analyze_project_coupling(
            input_param.project_path, input_param.exclude_patterns
        )
    except Exception as e:
        logger.error(f"Failed to analyze project coupling: {e}")
        return

    if project_metrics.module_count == 0:
        logger.warning("No Python modules found in the specified project.")
        return

    logger.info(f"Found {project_metrics.module_count} modules")

    # モジュールリストをフィルタリング
    filtered_modules = _filter_modules(project_metrics.module_metrics, filter_param)

    if not filtered_modules:
        logger.warning(
            f"No modules match the filter criteria: {filter_param.filter_type}"
        )
        return

    logger.info(f"Filtered to {len(filtered_modules)} modules")

    # 表示用のDataFrameに変換
    display_df = _transform_for_display(filtered_modules, display_param.columns)

    # ソート
    display_df = _sort_dataframe(
        display_df, display_param.sort_column, display_param.sort_desc
    )

    # 行数制限
    display_df = head_for_display(display_df, display_param.limit)

    # プロジェクトサマリーの表示（オプション）
    if display_param.show_summary:
        summary_df = _create_summary_display(project_metrics)
        print("=== プロジェクトサマリー ===")
        display(summary_df, display_param.format)
        print("\n=== モジュール結合度 ===")

    # 結果の表示
    display(display_df, display_param.format)

    # 結果のエクスポート
    if export_param.with_export():
        try:
            export(display_df, export_param.export_file_path, export_param.overwrite)
            logger.info(f"Results exported to: {export_param.export_file_path}")
        except Exception as e:
            logger.error(f"Failed to export results: {e}")
