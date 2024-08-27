import click

from pycodemetrics.cli.analyze_hotspot.cli import (
    hotspot as analyze_hotspot_metrics,
)
from pycodemetrics.cli.analyze_python.cli import (
    analyze as analyze_python_metrics,
)
from pycodemetrics.cli.sandbox import test


@click.group()
def cli():
    pass


cli.add_command(analyze_python_metrics)
cli.add_command(analyze_hotspot_metrics)
cli.add_command(test)


if __name__ == "__main__":
    cli()
