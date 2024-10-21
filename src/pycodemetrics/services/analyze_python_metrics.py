import logging
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from pycodemetrics.config.config_manager import UserGroupConfig
from pycodemetrics.metrics.py.python_metrics import PythonCodeMetrics, compute_metrics
from pycodemetrics.util.file_util import CodeType, get_code_type, get_group_name

logger = logging.getLogger(__name__)


class FilterCodeType(str, Enum):
    """
    Filter code type.

    PRODUCT: Filter product code.
    TEST: Filter test code.
    BOTH: Filter both product and test code.
    """

    PRODUCT = CodeType.PRODUCT.value
    TEST = CodeType.TEST.value
    BOTH = "both"

    @classmethod
    def to_list(cls) -> list[str]:
        """
        Returns:
            list code types.
        """
        return [e.value for e in cls]


class AnalyzePythonSettings(BaseModel, frozen=True, extra="forbid"):
    """
    Pythonファイルの解析設定を表すクラス。

    testcode_type_patterns (list[str]): テストコードのファイルパスパターン。
    user_groups (list[UserGroupConfig]): ユーザーが定義したグループ定義。
    """

    testcode_type_patterns: list[str] = []
    user_groups: list[UserGroupConfig] = []
    filter_code_type: FilterCodeType = FilterCodeType.PRODUCT


class PythonFileMetrics(BaseModel, frozen=True, extra="forbid"):
    """
    Pythonファイルのメトリクスを表すクラス。

    filepath (str): ファイルのパス。
    code_type (CodeType): プロダクトコードかテストコードかを示す。
    group_name (str): ユーザーが定義したグループ定義のどれに一致するか。
    metrics (PythonCodeMetrics): Pythonコードのメトリクス。
    """

    filepath: Path
    code_type: CodeType
    group_name: str
    metrics: PythonCodeMetrics

    def to_flat(self) -> dict[str, Any]:
        return {
            "filepath": self.filepath,
            "code_type": self.code_type.value,
            "group_name": self.group_name,
            **self.metrics.to_dict(),
        }

    @classmethod
    def get_keys(cls):
        keys = [k for k in cls.model_fields.keys() if k != "metrics"]
        keys.extend(PythonCodeMetrics.get_keys())
        return keys


def analyze_python_file(
    filepath: Path, settings: AnalyzePythonSettings
) -> PythonFileMetrics:
    """
    指定されたPythonファイルを解析し、そのメトリクスを計算します。

    Args:
        filepath (Path): 解析するPythonファイルのパス。
        settings (AnalyzePythonSettings): 解析の設定

    Returns:
        PythonFileMetrics: ファイルパス、ファイルタイプ、計算されたメトリクスを含むPythonFileMetricsオブジェクト。
    """
    code = _open(filepath)
    python_code_metrics = compute_metrics(code)
    return PythonFileMetrics(
        filepath=filepath,
        code_type=get_code_type(filepath, settings.testcode_type_patterns),
        group_name=get_group_name(filepath, settings.user_groups),
        metrics=python_code_metrics,
    )


def _open(filepath: Path) -> str:
    """
    指定されたファイルを開き、その内容を文字列として返します。

    Args:
        filepath (Path): 読み込むファイルのパス。

    Raises:
        ValueError: ファイルパスが設定されていない場合に発生。
        FileNotFoundError: ファイルが存在しない場合に発生。

    Returns:
        str: ファイルの内容を含む文字列。
    """
    if not filepath.exists():
        raise FileNotFoundError(f"{filepath} is not found")

    with open(filepath) as f:
        return f.read()
