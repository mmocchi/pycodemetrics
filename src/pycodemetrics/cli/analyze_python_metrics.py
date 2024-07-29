from pycodemetrics.services.analyze_python_metrics import analyze_python_file, PythonFileMetrics
from pycodemetrics.gitclient.gitcli import list_git_files

from tqdm import tqdm
import logging
import tabulate

logger = logging.getLogger(__name__)

def _get_target_files(repo_path: str) -> list[str]:
    return [f for f in list_git_files(repo_path) if f.endswith(".py")]

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

def run_analyze_python_metrics(repo_path: str):
    target_file_paths = _get_target_files(repo_path)
    results = _analyze_python_metrics(target_file_paths)

    return results