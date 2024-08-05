import sys
from pathlib import Path

import click
from pycodemetrics.cli import RETURN_CODE
from pycodemetrics.cli.analyze_hotspot.handler import (
    DisplayFormat,
    DisplayParameter,
    ExportParameter,
    InputTargetParameter,
    run_analyze_hotspot_metrics,
)


@click.command()
@click.argument("input_repo_path", type=click.Path(exists=True))
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
def hotspot(
    input_repo_path: str,
    format: str,
    export: str,
    export_overwrite: bool,
):
    """
    Analyze hotspot metrics in the specified path.

    INPUT_REPO_PATH: Path to the target directory of git repository.
    """

    try:
        input_param = InputTargetParameter(path=Path(input_repo_path))

        display_param = DisplayParameter(format=DisplayFormat(format))

        export_file_path = Path(export) if export else None
        export_param = ExportParameter(
            export_file_path=export_file_path, overwrite=export_overwrite
        )

        run_analyze_hotspot_metrics(input_param, display_param, export_param)
        sys.exit(RETURN_CODE.SUCCESS)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise e
