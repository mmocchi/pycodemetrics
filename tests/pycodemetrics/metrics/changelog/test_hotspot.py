import datetime as dt
from pathlib import Path

import pytest

from pycodemetrics.gitclient.models import GitFileCommitLog
from pycodemetrics.metrics.changelog.hotspot import HotspotMetrics, calculate_hotspot


def build_git_commit_log(commit_date: dt.datetime) -> GitFileCommitLog:
    return GitFileCommitLog(
        filepath=Path(""),
        commit_hash="",
        author="",
        commit_date=commit_date,
        message="",
    )


def test_calculate_hotspot():
    # Arrange
    gitlogs = [
        build_git_commit_log(commit_date=dt.datetime(2023, 1, 1)),
        build_git_commit_log(commit_date=dt.datetime(2023, 1, 2)),
        build_git_commit_log(commit_date=dt.datetime(2023, 1, 3)),
        build_git_commit_log(commit_date=dt.datetime(2023, 10, 4)),
    ]

    # Act
    result = calculate_hotspot(gitlogs)

    # Assert
    expected_first_commit_datetime = dt.datetime(2023, 1, 1)
    expected_last_commit_datetime = dt.datetime(2023, 10, 4)
    expected_change_count = 4

    assert result.first_commit_datetime == expected_first_commit_datetime
    assert result.last_commit_datetime == expected_last_commit_datetime
    assert result.change_count == expected_change_count
    assert result.lifetime_days == 276
    assert result.hotspot == 0.014492753623188406


def test_validate_first_commit_datetimeがlast_commit_datetimeよりも小さい():
    # 正常な日付のテスト

    # Act
    valid_metrics = HotspotMetrics(
        change_count=3,
        first_commit_datetime=dt.datetime(2023, 1, 1),
        last_commit_datetime=dt.datetime(2023, 1, 3),
    )

    # Assert
    assert valid_metrics.first_commit_datetime == dt.datetime(2023, 1, 1)
    assert valid_metrics.last_commit_datetime == dt.datetime(2023, 1, 3)


def test_validate_first_commit_datetimeがlast_commit_datetimeと同じ日時():
    # 正常な日付のテスト

    # Act
    valid_metrics = HotspotMetrics(
        change_count=3,
        first_commit_datetime=dt.datetime(2023, 1, 1),
        last_commit_datetime=dt.datetime(2023, 1, 1),
    )

    # Assert
    assert valid_metrics.first_commit_datetime == dt.datetime(2023, 1, 1)
    assert valid_metrics.last_commit_datetime == dt.datetime(2023, 1, 1)


def test_validate_first_commit_datetimeがlast_commit_datetimeよりも大きい():
    # 異常な日付のテスト

    # Act and Assert
    with pytest.raises(ValueError):
        HotspotMetrics(
            change_count=3,
            first_commit_datetime=dt.datetime(2023, 1, 3),
            last_commit_datetime=dt.datetime(2023, 1, 1),
        )
