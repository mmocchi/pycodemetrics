import logging
import sys
from pathlib import Path

import click

from pycodemetrics.cli import RETURN_CODE
from pycodemetrics.cli.analyze_committer.handler import (
    DisplayColumn,
    DisplayFormat,
    DisplayParameter,
    ExportParameter,
    InputTargetParameter,
    RuntimeParameter,
    run_analyze_committer_metrics,
)
from pycodemetrics.services.analyze_committer import FilterCodeType

logger = logging.getLogger(__name__)


@click.command()
@click.argument("input_repo_path", type=click.Path(exists=True))
@click.option(
    "--workers",
    type=int,
    default=None,
    help="Number of workers for parallel processing. Default: None. os.cpu_count() when None",
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
    default=10,
    help="Limit the number of files to display. Default: 10. And 0 means no limit.",
)
@click.option(
    "--code-type",
    type=click.Choice(FilterCodeType.to_list(), case_sensitive=True),
    default=FilterCodeType.PRODUCT.value,
    help=f"Filter code type, default: {FilterCodeType.PRODUCT.value}",
)
def committer(
    input_repo_path: str,
    workers: int | None,
    format: str,
    export: str,
    export_overwrite: bool,
    columns: str | None,
    limit: int,
    code_type: str,
):
    logger.info(
        f"Start analyze_committer_metrics. {input_repo_path=}, {workers=}, {format=}, {export=}, {export_overwrite=}"
    )

    try:
        # パラメータの設定
        input_param = InputTargetParameter(path=Path(input_repo_path))
        runtime_param = RuntimeParameter(
            workers=workers,
            filter_code_type=FilterCodeType(code_type),
        )
        column_list = (
            [DisplayColumn(c.strip()) for c in columns.split(",")] if columns else None
        )

        display_param = DisplayParameter(
            format=DisplayFormat(format),
            columns=column_list,
            limit=limit,
            filter_code_type=FilterCodeType(code_type),
        )

        logger.debug(
            f"RuntimeParameter: {runtime_param}, DisplayParameter: {display_param}"
        )

        export_file_path = Path(export) if export else None
        export_param = ExportParameter(
            export_file_path=export_file_path, overwrite=export_overwrite
        )

        # メイン処理の実行
        run_analyze_committer_metrics(
            input_param, runtime_param, display_param, export_param
        )

        logger.info("End analyze_hotspot_metrics. Success.")
        sys.exit(RETURN_CODE.SUCCESS)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise e
