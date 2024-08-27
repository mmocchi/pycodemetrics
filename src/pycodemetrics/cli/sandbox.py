from pathlib import Path

import click

from pycodemetrics.config.config_manager import ConfigManager


@click.command(hidden=True)
def test():
    print(ConfigManager.get_user_groups(Path("pyproject.toml")))
    print(ConfigManager.get_testcode_type_patterns(Path("pyproject.toml")))
