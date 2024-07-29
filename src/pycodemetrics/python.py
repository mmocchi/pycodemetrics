import os

import pandas as pd
from gitclient.gitcli import list_git_files
from tabulate import tabulate
from tqdm import tqdm

from pycodemetrics.metrics.py.python_metrics import compute_metrics

if __name__ == "__main__":
    # target_path = "/Users/akihiro_matsumoto/projects/hakari/hakari-backend"
    target_path = "."
    results = []

    target_files = [f for f in list_git_files(target_path) if f.endswith(".py")]
    for git_file_path in tqdm(target_files):
        full_file_path = os.path.join(target_path, git_file_path)

        metrics = {}
        results.append(compute_metrics(full_file_path).to_dict())

    result_df = pd.DataFrame(results, columns=results[0].keys())
    print(tabulate(result_df, headers="keys"))
