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


class AnalizeCommitterSettings(BaseModel, frozen=True, extra="forbid"):
    base_datetime: dt.datetime
    testcode_type_patterns: list[str] = []
    user_groups: list[UserGroupConfig] = []
    filter_code_type: FilterCodeType = FilterCodeType.PRODUCT


class CommitterChangeCount(BaseModel, frozen=True, extra="forbid"):
    committer: str
    change_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "committer": self.committer,
            "change_count": self.change_count,
        }


class FileChangeCountMetrics(BaseModel, frozen=True, extra="forbid"):
    filepath: Path
    change_counts: list[CommitterChangeCount]

    def to_flatten_list(self) -> list[dict[str, Any]]:
        results = []
        for change_count in self.change_counts:
            results.append(
                {
                    "filepath": self.filepath,
                    "committer": change_count.committer,
                    "change_count": change_count.change_count,
                }
            )
        return results


def aggregate_changecount_by_committer(
    filepath: Path, repo_dir_path: Path, settings: AnalizeCommitterSettings
) -> FileChangeCountMetrics:
    gitlogs = parse_gitlogs(filepath, get_file_gitlogs(filepath, repo_dir_path))

    changecounter = Counter([gitlog.author for gitlog in gitlogs])

    # CounterからCommitterChangeCountに変換
    changecount_by_committer = [
        CommitterChangeCount(committer=k, change_count=v)
        for k, v in changecounter.items()
    ]

    return FileChangeCountMetrics(
        filepath=filepath, change_counts=changecount_by_committer
    )
