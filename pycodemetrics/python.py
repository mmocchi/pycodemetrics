from gitclient.gitcli import list_git_files

from pycodemetrics.radon_wrapper import (
    get_block_complexity,
    get_complexity,
    get_maintainability_index,
    get_raw_metrics,
)

if __name__ == "__main__":
    for git_file_path in list_git_files():
        if not git_file_path.endswith(".py"):
            continue

        print(git_file_path)
        print(get_raw_metrics(git_file_path))
        print(get_complexity(git_file_path))
        print(get_block_complexity(git_file_path))
        print(get_maintainability_index(git_file_path))
        print("*" * 10)
