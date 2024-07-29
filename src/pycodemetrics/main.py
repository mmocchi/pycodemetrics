import click

from pycodemetrics.services.analyze_python_metrics import analyze_git_repo


@click.group()
def cli():
    pass


@click.command()
def analyze():
    analyze_git_repo(".")


cli.add_command(analyze)

if __name__ == "__main__":
    cli()
