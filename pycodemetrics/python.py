from gitclient.gitcli import get_gitlogs, list_git_files
from gitclient.gitlog_parser import parse_gitlogs

if __name__ == "__main__":
    for git_file_path in list_git_files():
        if not git_file_path.endswith(".py"):
            continue

        rawlog = get_gitlogs(git_file_path)
        parsed_logs = parse_gitlogs(git_file_path, rawlog)
        for parsed_log in parsed_logs:
            print(parsed_log)
