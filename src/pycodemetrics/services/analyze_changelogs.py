import datetime as dt
from pathlib import Path

from pydantic import BaseModel

from pycodemetrics.config.config_manager import UserGroupConfig
from pycodemetrics.gitclient.gitcli import get_file_gitlogs
from pycodemetrics.gitclient.gitlog_parser import parse_gitlogs
from pycodemetrics.metrics.changelog.hotspot import HotspotMetrics, calculate_hotspot
from pycodemetrics.util.file_util import CodeType, get_code_type, get_group_name


class AnalizeChangeLogSettings(BaseModel, frozen=True):
    base_datetime: dt.datetime
    testcode_type_patterns: list[str] = []
    user_groups: list[UserGroupConfig] = []


class FileHotspotMetrics(BaseModel, frozen=True):
    filepath: Path
    code_type: CodeType
    group_name: str
    hotspot: HotspotMetrics

    def to_flat(self) -> dict:
        return {
            "filepath": self.filepath,
            "code_type": self.code_type.value,
            "group_name": self.group_name,
            **self.hotspot.to_dict(),
        }

    @classmethod
    def get_keys(cls):
        keys = [k for k in cls.model_fields.keys() if k != "hotspot"]
        keys.extend(HotspotMetrics.get_keys())
        return keys


def analyze_changelogs_file(
    filepath: Path, repo_dir_path: Path, settings: AnalizeChangeLogSettings
) -> FileHotspotMetrics:
    """
    指定されたパスのGitのコミットLogを解析し、メトリクスを計算します。

    Args:
        filepath (Path): 解析するファイルのパス。
        repo_dir_path (Path): Gitリポジトリのパス
        settings (AnalizeChangeLogSettings): 解析の設定

    Returns:
        FileHotspotMetrics: ファイルパス、計算されたメトリクスを含むFileHotspotMetricsオブジェクト。
    """

    gitlogs = parse_gitlogs(filepath, get_file_gitlogs(filepath, repo_dir_path))
    if len(gitlogs) == 0:
        raise ValueError("No git logs.")

    hotspot_metrics = calculate_hotspot(gitlogs, settings.base_datetime)

    return FileHotspotMetrics(
        filepath=filepath,
        code_type=get_code_type(filepath, settings.testcode_type_patterns),
        group_name=get_group_name(filepath, settings.user_groups),
        hotspot=hotspot_metrics,
    )
