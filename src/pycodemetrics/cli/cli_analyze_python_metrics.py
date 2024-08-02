import logging
import os

import pandas as pd
import tabulate
from tqdm import tqdm

from pycodemetrics.services.analyze_python_metrics import (
    PythonFileMetrics,
    analyze_python_file,
)
from pycodemetrics.util.file_util import (
    get_target_files_by_git_ls_files,
    get_target_files_by_path,
)

logger = logging.getLogger(__name__)


def _analyze_python_metrics(target_file_paths: list[str]) -> list[PythonFileMetrics]:
    results = []
    for filepath in tqdm(target_file_paths):
        if not filepath.endswith(".py"):
            logger.warning(f"Skipping {filepath} as it is not a python file")
            continue

        try:
            result = analyze_python_file(filepath)
            results.append(result)
        except Exception as e:
            logger.warning(f"Skipping {filepath}. cause of error: {e}")
            continue
    return results


def _transform_for_display(results: list[PythonFileMetrics]) -> pd.DataFrame:
    results_flat = [result.to_flat() for result in results]
    return pd.DataFrame(results_flat, columns=results_flat[0].keys())


def run_analyze_python_metrics(path: str, with_git_repo: bool = False):
    if with_git_repo:
        target_file_paths = get_target_files_by_git_ls_files(path)
        base_path = path
    else:
        target_file_paths = get_target_files_by_path(path)
        base_path = "."

    if len(target_file_paths) == 0:
        logger.warning("No python files found in the specified path.")
        return

    target_file_full_paths = [os.path.join(base_path, f) for f in target_file_paths]
    results = _analyze_python_metrics(target_file_full_paths)

    results_df = _transform_for_display(results)
    results_df["filepath"] = results_df["filepath"].map(
        lambda x: os.path.relpath(x, base_path)
    )
    result_table = tabulate.tabulate(results_df, headers="keys")  # type: ignore
    print(result_table)
