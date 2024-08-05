from pathlib import Path

from pydantic import BaseModel

from pycodemetrics.gitclient.gitcli import get_file_gitlogs
from pycodemetrics.gitclient.gitlog_parser import parse_gitlogs
from pycodemetrics.metrics.changelog.hotspot import HotspotMetrics, calculate_hotspot


class FileHotspotMetrics(BaseModel, frozen=True):
    filepath: Path
    hotspot: HotspotMetrics

    def to_flat(self):
        return {
            "filepath": self.filepath,
            **self.hotspot.to_dict(),
        }


def analyze_changelogs_file(filepath: Path) -> FileHotspotMetrics:
    """
    指定されたパスのGitのコミットLogを解析し、メトリクスを計算します。

    Args:
        filepath (Path): 解析するファイルのパス。

    Returns:
        FileHotspotMetrics: ファイルパス、計算されたメトリクスを含むFileHotspotMetricsオブジェクト。
    """

    gitlogs = parse_gitlogs(filepath, get_file_gitlogs(filepath))

    hotspot_metrics = calculate_hotspot(gitlogs)

    return FileHotspotMetrics(
        filepath=filepath,
        hotspot=hotspot_metrics,
    )
