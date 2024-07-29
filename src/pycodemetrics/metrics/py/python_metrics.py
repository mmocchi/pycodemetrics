from dataclasses import asdict, dataclass

from pycodemetrics.metrics.py.cognitive_complexity import get_cognitive_complexity
from pycodemetrics.metrics.py.import_analyzer import analyze_import_counts
from pycodemetrics.metrics.py.raw.radon_wrapper import (
    get_complexity,
    get_maintainability_index,
    get_raw_metrics,
)


@dataclass
class PythonCodeMetrics:
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

    def to_dict(self):
        return asdict(self)


def compute_metrics(code: str) -> PythonCodeMetrics:
    metrics = {}
    metrics.update(get_raw_metrics(code))
    metrics["import_count"] = analyze_import_counts(code)
    metrics["cyclomatic_complexity"] = get_complexity(code)
    metrics["maintainability_index"] = get_maintainability_index(code)
    metrics["cognitive_complexity"] = get_cognitive_complexity(code)

    return PythonCodeMetrics(**metrics)
