from pathlib import Path
from typing import Any

import toml
from pydantic import BaseModel


class UserGroupConfig(BaseModel, extra="forbid"):
    """
    User group configuration.

    name (str): The name of the user group.
    patterns (list[str]): The patterns of the user group.
    """

    name: str
    patterns: list[str]


TESTCODE_PATTERN_DEFAULT: list[str] = ["*/tests/*.*", "*/tests/*/*.*", "tests/*.*"]
USER_GROUPS_DEFAULT: list[UserGroupConfig] = []


class ConfigManager:
    """
    Configuration manager for pycodemetrics.

    This class loads the configuration from the pyproject.toml file.
    """

    @classmethod
    def _load_user_groups(cls, pyproject_toml: dict) -> list[UserGroupConfig]:
        """
        Load the user groups from the pyproject.toml file.

        Args:
            pyproject_toml (dict): The pyproject.toml file.

        Returns:
            list[UserGroupConfig]: The user group configuration
        """
        try:
            user_group_dict = pyproject_toml["tool"]["pycodemetrics"]["groups"]["user"]
            return [
                UserGroupConfig(
                    name=k,
                    patterns=v,
                )
                for k, v in user_group_dict.items()
            ]
        except KeyError:
            return USER_GROUPS_DEFAULT

    @classmethod
    def _load_testcode_pattern(cls, pyproject_toml: dict) -> list[str]:
        """
        Load the testcode pattern from the pyproject.toml file.

        Args:
            pyproject_toml (dict): The pyproject.toml file.

        Returns:
            list[str]: The testcode pattern.
        """
        try:
            return pyproject_toml["tool"]["pycodemetrics"]["groups"]["testcode"][
                "pattern"
            ]
        except KeyError:
            return TESTCODE_PATTERN_DEFAULT

    @classmethod
    def _load(cls, config_path: Path) -> dict[str, Any]:
        """
        Load the pyproject.toml file.

        Args:
            config_path (Path): The path to the pyproject.toml file.

        Returns:
            dict[str, Any]: The pyproject.toml file.
        """

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        pyproject_toml = toml.load(config_path)
        return pyproject_toml

    @classmethod
    def get_testcode_type_patterns(cls, config_file_path: Path) -> list[str]:
        """
        Get the patterns for testcode.

        Args:
            config_file_path (Path): The path to the configuration file.

        Returns:
            list[str]: The testcode patterns.
        """
        try:
            pyproject_toml = cls._load(config_file_path)
            return cls._load_testcode_pattern(pyproject_toml)
        except FileNotFoundError:
            return TESTCODE_PATTERN_DEFAULT

    @classmethod
    def get_user_groups(cls, config_file_path: Path) -> list[UserGroupConfig]:
        """
        Get the user groups.

        Args:
            config_file_path (Path): The path to the configuration file.

            Returns:
                list[UserGroupConfig]: The user group configuration.
        """
        try:
            pyproject_toml = cls._load(config_file_path)
            return cls._load_user_groups(pyproject_toml)
        except FileNotFoundError:
            return USER_GROUPS_DEFAULT
