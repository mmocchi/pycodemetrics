import fnmatch
from dataclasses import dataclass

from pycodemetrics.metrics.py.cc_wrapper import get_function_cognitive_complexity
from pycodemetrics.metrics.py.radon_wrapper import (
    get_complexity,
    get_maintainability_index,
    get_raw_metrics,
)


@dataclass
class PythonMetrics:
    file_path: str
    lines_of_code: int
    logical_lines_of_code: int
    source_lines_of_code: int
    comments: int
    single_comments: int
    multi: int
    blank: int
    cyclomatic_complexity: int
    maintainability_index: float
    cognitive_complexity: int
    product_or_test: str

    def to_dict(self):
        return {
            "file_path": self.file_path,
            "lines_of_code": self.lines_of_code,
            "logical_lines_of_code": self.logical_lines_of_code,
            "source_lines_of_code": self.source_lines_of_code,
            "comments": self.comments,
            "single_comments": self.single_comments,
            "multi": self.multi,
            "blank": self.blank,
            "cyclomatic_complexity": self.cyclomatic_complexity,
            "maintainability_index": self.maintainability_index,
            "cognitive_complexity": self.cognitive_complexity,
            "product_or_test": self.product_or_test,
        }


def _is_tests_file(filepath: str) -> bool:
    return fnmatch.fnmatch(filepath, "**/tests*/**/*.*") or fnmatch.fnmatch(
        filepath, "**/tests*/*.*"
    )


def get_product_or_test(filepath: str) -> str:
    if _is_tests_file(filepath):
        return "test"
    return "product"


def get_cognitive_complexity(filepath: str) -> int:
    cognitive_complexity = get_function_cognitive_complexity(filepath)
    return sum(c.complexity for c in cognitive_complexity)


def compute_metrics(filepath: str) -> PythonMetrics:
    metrics = {}
    metrics["file_path"] = filepath
    metrics.update(get_raw_metrics(filepath))
    metrics["cyclomatic_complexity"] = get_complexity(filepath)
    metrics["maintainability_index"] = get_maintainability_index(filepath)
    metrics["cognitive_complexity"] = get_cognitive_complexity(filepath)
    metrics["product_or_test"] = get_product_or_test(filepath)

    return PythonMetrics(**metrics)
