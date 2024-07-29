import fnmatch
from dataclasses import dataclass, asdict

from pycodemetrics.metrics.py.cc_wrapper import get_function_cognitive_complexity
from pycodemetrics.metrics.py.radon_wrapper import (
    get_complexity,
    get_maintainability_index,
    get_raw_metrics,
)
from pycodemetrics.metrics.py.import_analyzer import analyze_import_counts


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
    import_count: int
    cyclomatic_complexity: int
    maintainability_index: float
    cognitive_complexity: int
    product_or_test: str

    def to_dict(self):
        return asdict(self)


def _is_tests_file(filepath: str) -> bool:
    # 下記がすべてマッチするワイルドカードを生成してください。
    # * tests/test_aaa.py
    # * abc/tests/bbb.py
    # * abc/3234/tests/_faefae.py
    # * abc/tests/abcde/faeefa.py

    patterns = ["*/tests/*.*", "*/tests/*/*.*", "tests/*.*"]
    return any(fnmatch.fnmatch(filepath, pattern) for pattern in patterns)

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
    metrics["import_count"] = analyze_import_counts(filepath)
    metrics["cyclomatic_complexity"] = get_complexity(filepath)
    metrics["maintainability_index"] = get_maintainability_index(filepath)
    metrics["cognitive_complexity"] = get_cognitive_complexity(filepath)
    metrics["product_or_test"] = get_product_or_test(filepath)

    return PythonMetrics(**metrics)
