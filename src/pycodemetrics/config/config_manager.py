import os
from pathlib import Path

import toml
from pydantic import BaseModel


class UserGroupConfig(BaseModel):
    name: str
    patterns: list[str]


TESTCODE_PATTERN_DEFAULT: list[str] = ["*/tests/*.*", "*/tests/*/*.*", "tests/*.*"]
USER_GROUPS_DEFAULT: list[UserGroupConfig] = []


class ConfigManager:
    @classmethod
    def _load_user_groups(cls, pyproject_toml):
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
    def _load_testcode_pattern(cls, pyproject_toml):
        try:
            return pyproject_toml["tool"]["pycodemetrics"]["groups"]["testcode"][
                "pattern"
            ]
        except KeyError:
            return TESTCODE_PATTERN_DEFAULT

    @classmethod
    def _load(cls, config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        pyproject_toml = toml.load(config_path)
        return pyproject_toml

    @classmethod
    def get_testcode_type_patterns(cls, config_file_path: Path) -> list[str]:
        try:
            pyproject_toml = cls._load(config_file_path)
            return cls._load_testcode_pattern(pyproject_toml)
        except FileNotFoundError:
            return TESTCODE_PATTERN_DEFAULT

    @classmethod
    def get_user_groups(cls, config_file_path: Path) -> list[UserGroupConfig]:
        try:
            pyproject_toml = cls._load(config_file_path)
            return cls._load_user_groups(pyproject_toml)
        except FileNotFoundError:
            return USER_GROUPS_DEFAULT
