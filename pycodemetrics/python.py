import fnmatch
import os

import pandas as pd
from gitclient.gitcli import list_git_files
from tabulate import tabulate
from tqdm import tqdm

from pycodemetrics.metrics.py.cc_wrapper import compute_cognitive_complexity
from pycodemetrics.metrics.py.radon_wrapper import (
    get_complexity,
    get_maintainability_index,
    get_raw_metrics,
)


def is_tests_file(filepath: str) -> bool:
    return fnmatch.fnmatch(filepath, "**/tests*/**/*.*") or fnmatch.fnmatch(
        filepath, "**/tests*/*.*"
    )


def get_product_or_test(filepath: str) -> str:
    if is_tests_file(filepath):
        return "test"
    return "product"


if __name__ == "__main__":
    # target_path = "/Users/akihiro_matsumoto/projects/hakari/hakari-backend"
    target_path = "."
    results = []

    target_files = [f for f in list_git_files(target_path) if f.endswith(".py")]
    for git_file_path in tqdm(target_files):
        full_file_path = os.path.join(target_path, git_file_path)

        metrics = {}
        metrics["file_path"] = git_file_path
        metrics.update(get_raw_metrics(full_file_path))
        metrics["Cyclomatic Complexity"] = get_complexity(full_file_path)
        metrics["Maintainability Index"] = get_maintainability_index(full_file_path)
        metrics["product_or_test"] = get_product_or_test(git_file_path)

        results.append(metrics)

        print(compute_cognitive_complexity(full_file_path))

    result_df = pd.DataFrame(results, columns=results[0].keys())
    result_df.to_csv("20240723_hakari-backend_codemetrics.csv", index=False)
    print(tabulate(result_df, headers="keys"))
