import click

from pycodemetrics.cli.analyze_python_metrics import run_analyze_python_metrics


@click.group()
def cli():
    pass


@click.command()
def analyze():
    run_analyze_python_metrics(".")


cli.add_command(analyze)

if __name__ == "__main__":
    cli()
