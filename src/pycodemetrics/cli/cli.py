import click

from pycodemetrics.cli.cli_analyze_python_metrics import run_analyze_python_metrics


@click.group()
def cli():
    pass


@click.command()
@click.option(
    "--dir_path",
    default=".",
    help="Directory path to analyze. Default is current directory.",
)
def analyze(dir_path: str):
    run_analyze_python_metrics(dir_path)


cli.add_command(analyze)

if __name__ == "__main__":
    cli()
