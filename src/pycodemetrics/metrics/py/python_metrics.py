from pydantic import BaseModel

from pycodemetrics.metrics.py.cognitive_complexity import get_cognitive_complexity
from pycodemetrics.metrics.py.import_analyzer import analyze_import_counts
from pycodemetrics.metrics.py.raw.radon_wrapper import (
    get_complexity,
    get_maintainability_index,
    get_raw_metrics,
)


class PythonCodeMetrics(BaseModel, frozen=True, extra="forbid"):
    """
    Pythonコードのメトリクスを表すクラス。

    Attributes:
        lines_of_code (int): コードの行数。
        logical_lines_of_code (int): 論理行数。
        source_lines_of_code (int): ソースコードの行数。
        comments (int): コメントの行数。
        single_comments (int): 単一行コメントの数。
        multi (int): 複数行コメントの数。
        blank (int): 空行の数。
        import_count (int): インポート文の数。
        cyclomatic_complexity (int): 循環的複雑度。
        maintainability_index (float): 保守性指数。
        cognitive_complexity (int): 認知的複雑度。
    """

    lines_of_code: int
    logical_lines_of_code: int
    source_lines_of_code: int
    comments: int
    single_comments: int
    multi: int
    blank: int
    import_count: int
    cyclomatic_complexity: int
    maintainability_index: float
    cognitive_complexity: int

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def get_keys(cls):
        return cls.model_fields.keys()


def compute_metrics(code: str) -> PythonCodeMetrics:
    """
    与えられたPythonコードのメトリクスを計算します。

    Args:
        code (str): メトリクスを計算するPythonコード。

    Returns:
        PythonCodeMetrics: 計算されたメトリクスを含むPythonCodeMetricsオブジェクト。
    """
    metrics = {}
    metrics.update(get_raw_metrics(code).to_dict())
    metrics["import_count"] = analyze_import_counts(code)
    metrics["cyclomatic_complexity"] = get_complexity(code)
    metrics["maintainability_index"] = get_maintainability_index(code)
    metrics["cognitive_complexity"] = get_cognitive_complexity(code)

    return PythonCodeMetrics(**metrics)
