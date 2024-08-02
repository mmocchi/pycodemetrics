from enum import IntEnum
from pathlib import Path

import click

from pycodemetrics.cli.cli_analyze_python_metrics import (
    InputTargetParameter,
    run_analyze_python_metrics,
)


class RETURN_CODE(IntEnum):
    SUCCESS = 0
    ERROR = 1


@click.group()
def cli():
    pass


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option(
    "--with-git-repo",
    is_flag=True,
    default=False,
    help="Analyze python files in the git",
)
def analyze(input_path: str, with_git_repo: bool):
    """
    Analyze python metrics in the specified path.

    INPUT_PATH: Path to the target python file or directory.
    """

    input_param = InputTargetParameter(
        path=Path(input_path), with_git_repo=with_git_repo
    )

    run_analyze_python_metrics(input_param)


cli.add_command(analyze)

if __name__ == "__main__":
    try:
        cli()
        exit(RETURN_CODE.SUCCESS)
    except Exception as e:
        print(f"Error: {e}")
        exit(RETURN_CODE.ERROR)
