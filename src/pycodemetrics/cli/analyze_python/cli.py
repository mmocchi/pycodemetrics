import sys
from pathlib import Path

import click

from pycodemetrics.cli import RETURN_CODE
from pycodemetrics.cli.analyze_python.handler import (
    Column,
    DisplayFormat,
    DisplayParameter,
    ExportParameter,
    InputTargetParameter,
    run_analyze_python_metrics,
)
from pycodemetrics.services.analyze_python_metrics import FilterCodeType


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option(
    "--with-git-repo",
    is_flag=True,
    default=False,
    help="Analyze python files in the git",
)
@click.option(
    "--format",
    type=click.Choice(DisplayFormat.to_list(), case_sensitive=True),
    default=DisplayFormat.TABLE.value,
    help=f"Output format, default: {DisplayFormat.TABLE.value}",
)
@click.option(
    "--export",
    type=click.Path(file_okay=True, dir_okay=False),
    default=None,
    help="Export the result to the specified file path. If not specified, do not export.",
)
@click.option(
    "--export-overwrite",
    is_flag=True,
    default=False,
    help="Overwrite the export file if it already exists.",
)
@click.option(
    "--columns",
    type=str,
    default=None,
    help="Columns to display. Default: None. When None, display all columns.",
)
@click.option(
    "--limit",
    type=click.IntRange(min=0),
    default=0,
    help="Limit the number of files to display. Default: 10. And 0 means no limit.",
)
@click.option(
    "--code-type",
    type=click.Choice(FilterCodeType.to_list(), case_sensitive=True),
    default=FilterCodeType.PRODUCT.value,
    help=f"Filter code type, default: {FilterCodeType.PRODUCT.value}",
)
def analyze(
    input_path: str,
    with_git_repo: bool,
    format: str,
    export: str,
    export_overwrite: bool,
    columns: str | None,
    limit: int,
    code_type: str,
):
    """
    Analyze python metrics in the specified path.

    INPUT_PATH: Path to the target python file or directory.
    """

    try:
        # パラメータの設定
        input_param = InputTargetParameter(
            path=Path(input_path), with_git_repo=with_git_repo
        )

        column_list = (
            [Column(c.strip()) for c in columns.split(",")] if columns else None
        )

        display_param = DisplayParameter(
            format=DisplayFormat(format),
            columns=column_list,
            limit=limit,
            filter_code_type=FilterCodeType(code_type),
        )

        export_file_path = Path(export) if export else None
        export_param = ExportParameter(
            export_file_path=export_file_path, overwrite=export_overwrite
        )

        # メイン処理の実行
        run_analyze_python_metrics(input_param, display_param, export_param)
        sys.exit(RETURN_CODE.SUCCESS)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise e
