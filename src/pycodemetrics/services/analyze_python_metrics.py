import fnmatch
import logging
import os
from dataclasses import dataclass

from pycodemetrics.gitclient.gitcli import list_git_files
from pycodemetrics.metrics.py.python_metrics import PythonCodeMetrics, compute_metrics

logger = logging.getLogger(__name__)


@dataclass
class PythonFileMetrics:
    filepath: str
    product_or_test: str
    metrics: PythonCodeMetrics


def analyze_git_repo(repo_path: str) -> list[PythonFileMetrics]:
    target_files = [f for f in list_git_files(repo_path) if f.endswith(".py")]
    return analyze_python_files(target_files)


def analyze_python_files(filepath_list: list[str]) -> list[PythonFileMetrics]:
    results = []
    for filepath in filepath_list:
        if not filepath.endswith(".py"):
            logger.warning(f"Skipping {filepath} as it is not a python file")

        try:
            results.append(analyze_python_file(filepath))
        except Exception as e:
            logger.warning(f"Skipping {filepath} cause of error: {e}")
    return results


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

    with open(filepath, "r") as f:
        return f.read()
