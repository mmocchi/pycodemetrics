import fnmatch
import logging
import os
from dataclasses import dataclass

from pycodemetrics.metrics.py.python_metrics import PythonCodeMetrics, compute_metrics

logger = logging.getLogger(__name__)


@dataclass
class PythonFileMetrics:
    filepath: str
    product_or_test: str
    metrics: PythonCodeMetrics

    def to_flat(self):
        return {
            "filepath": self.filepath,
            "product_or_test": self.product_or_test,
            **self.metrics.to_dict(),
        }

def analyze_python_file(filepath: str):
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


def get_product_or_test(filepath: str) -> str:
    if _is_tests_file(filepath):
        return "test"
    return "product"


def _open(filepath: str) -> str:
    if not filepath:
        raise ValueError("filepath must be set")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath} is not found")

    with open(filepath) as f:
        return f.read()
