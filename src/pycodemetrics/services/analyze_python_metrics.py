import fnmatch
import logging
import os
from enum import Enum

from pydantic import BaseModel

from pycodemetrics.metrics.py.python_metrics import PythonCodeMetrics, compute_metrics

logger = logging.getLogger(__name__)

class CodeType(Enum):
    PRODUCT = "product"
    TEST = "test"


class PythonFileMetrics(BaseModel, frozen=True):
    """
    Pythonファイルのメトリクスを表すクラス。

    属性:
        filepath (str): ファイルのパス。
        product_or_test (CodeType): プロダクトコードかテストコードかを示す。
        metrics (PythonCodeMetrics): Pythonコードのメトリクス。
    """
    filepath: str
    product_or_test: CodeType
    metrics: PythonCodeMetrics

    def to_flat(self):
        return {
            "filepath": self.filepath,
            "product_or_test": self.product_or_test.value,
            **self.metrics.to_dict(),
        }

def analyze_python_file(filepath: str):
    """
    指定されたPythonファイルを解析し、そのメトリクスを計算します。

    Args:
        filepath (str): 解析するPythonファイルのパス。

    Returns:
        PythonFileMetrics: ファイルパス、ファイルタイプ、計算されたメトリクスを含むPythonFileMetricsオブジェクト。
    """
    code = _open(filepath)
    python_code_metrics = compute_metrics(code)
    return PythonFileMetrics(
        filepath=filepath,
        product_or_test=get_product_or_test(filepath),
        metrics=python_code_metrics,
    )


def _is_tests_file(filepath: str) -> bool:
    patterns = ["*/tests/*.*", "*/tests/*/*.*", "tests/*.*"]
    return any(fnmatch.fnmatch(filepath, pattern) for pattern in patterns)


def get_product_or_test(filepath: str) -> CodeType:
    if _is_tests_file(filepath):
        return CodeType.TEST
    return CodeType.PRODUCT


def _open(filepath: str) -> str:
    """
    指定されたファイルを開き、その内容を文字列として返します。

    Args:
        filepath (str): 読み込むファイルのパス。

    Raises:
        ValueError: ファイルパスが設定されていない場合に発生。
        FileNotFoundError: ファイルが存在しない場合に発生。

    Returns:
        str: ファイルの内容を含む文字列。
    """
    if not filepath:
        raise ValueError("filepath must be set")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath} is not found")

    with open(filepath) as f:
        return f.read()
