import datetime as dt
from collections import Counter
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from pycodemetrics.config.config_manager import UserGroupConfig
from pycodemetrics.gitclient.gitcli import get_file_gitlogs
from pycodemetrics.gitclient.gitlog_parser import parse_gitlogs
from pycodemetrics.util.file_util import CodeType


class FilterCodeType(str, Enum):
    """
    Filter code type.

    PRODUCT: Filter product code.
    TEST: Filter test code.
    BOTH: Filter both product and test code.
    """

    PRODUCT = CodeType.PRODUCT.value
    TEST = CodeType.TEST.value
    BOTH = "both"

    @classmethod
    def to_list(cls) -> list[str]:
        """
        Returns:
            list code types.
        """
        return [e.value for e in cls]


class AnalizeCommittierSettings(BaseModel, frozen=True, extra="forbid"):
    base_datetime: dt.datetime
    testcode_type_patterns: list[str] = []
    user_groups: list[UserGroupConfig] = []
    filter_code_type: FilterCodeType = FilterCodeType.PRODUCT


class FileChangeCountMetrics(BaseModel, frozen=True, extra="forbid"):
    filepath: Path
    change_count: Counter

    def to_flat(self) -> dict[str, Any]:
        return {
            "filepath": self.filepath,
            **dict(self.change_count),
        }

    @classmethod
    def get_keys(cls):
        keys = [k for k in cls.model_fields.keys()]
        return keys


def aggregate_changecount_by_commiter(
    filepath: Path, repo_dir_path: Path, settings: AnalizeCommittierSettings
) -> FileChangeCountMetrics:
    gitlogs = parse_gitlogs(filepath, get_file_gitlogs(filepath, repo_dir_path))

    changecount_by_commiter = Counter([gitlog.author for gitlog in gitlogs])
    return FileChangeCountMetrics(
        filepath=filepath, change_count=changecount_by_commiter
    )
