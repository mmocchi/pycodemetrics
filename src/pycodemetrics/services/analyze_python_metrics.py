import logging
from pathlib import Path

from pydantic import BaseModel

from pycodemetrics.config.config_manager import UserGroupConfig
from pycodemetrics.metrics.py.python_metrics import PythonCodeMetrics, compute_metrics
from pycodemetrics.util.file_util import CodeType, get_code_type, get_group_name

logger = logging.getLogger(__name__)


class AnalyzePythonSettings(BaseModel, frozen=True, extra="forbid"):
    testcode_type_patterns: list[str] = []
    user_groups: list[UserGroupConfig] = []


class PythonFileMetrics(BaseModel, frozen=True, extra="forbid"):
    """
    Pythonファイルのメトリクスを表すクラス。

    属性:
        filepath (str): ファイルのパス。
        code_type (CodeType): プロダクトコードかテストコードかを示す。
        group_name (str): ユーザーが定義したグループ定義のどれに一致するか。
        metrics (PythonCodeMetrics): Pythonコードのメトリクス。
    """

    filepath: Path
    code_type: CodeType
    group_name: str
    metrics: PythonCodeMetrics

    def to_flat(self):
        return {
            "filepath": self.filepath,
            "code_type": self.code_type.value,
            "group_name": self.group_name,
            **self.metrics.to_dict(),
        }


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
