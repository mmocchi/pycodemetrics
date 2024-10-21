import datetime as dt
import math
from typing import Self

from pydantic import BaseModel, computed_field, model_validator

from pycodemetrics.gitclient.models import GitFileCommitLog


class HotspotMetrics(BaseModel, frozen=True, extra="forbid"):
    """
    Hotspot metrics.

    change_count (int): The number of changes.
    first_commit_datetime (dt.datetime): The first commit datetime.
    last_commit_datetime (dt.datetime): The last commit datetime.
    base_datetime (dt.datetime): The base datetime.
    hotspot (float): The hotspot metric.
    """

    change_count: int
    first_commit_datetime: dt.datetime
    last_commit_datetime: dt.datetime
    base_datetime: dt.datetime
    hotspot: float

    @model_validator(mode="after")
    def validate_commit_dates(self) -> Self:
        if self.first_commit_datetime > self.last_commit_datetime:
            raise ValueError(
                "first_commit_datetime must be less than last_commit_datetime"
            )
        return self

    @computed_field(return_type=int)  # type: ignore
    @property
    def lifetime_days(self):
        return (self.base_datetime - self.first_commit_datetime).days

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def get_keys(cls):
        return cls.model_fields.keys()


def _calculate_t(
    first_commit_datetime: dt.datetime,
    last_commit_datetime: dt.datetime,
    commit_date: dt.datetime,
    base_datetime: dt.datetime,
) -> float:
    t = 1 - (
        (base_datetime - commit_date).total_seconds()
        / (base_datetime - first_commit_datetime).total_seconds()
    )
    return t


def calculate_hotspot(
    gitlogs: list[GitFileCommitLog], base_datetime: dt.datetime
) -> HotspotMetrics:
    """
    Calculate the hotspot metric.

    Args:
        gitlogs (list[GitFileCommitLog]): A list of GitFileCommitLog.
        settings (HotspotCalculatorSettings): The settings for the hotspot calculator.

    Returns:
        float: The hotspot metric.
    """

    num_of_changes = len(gitlogs)
    if num_of_changes == 0:
        raise ValueError("The number of changes must be greater than 0.")

    first_commit_datetime = min([log.commit_date for log in gitlogs])
    last_commit_datetime = max([log.commit_date for log in gitlogs])

    base_datetime_ = base_datetime
    if base_datetime_ == last_commit_datetime:
        base_datetime_ += dt.timedelta(seconds=1)

    hotspots: float = 0
    for log in gitlogs:
        t = _calculate_t(
            first_commit_datetime, last_commit_datetime, log.commit_date, base_datetime_
        )
        exp_input = (-12 * t) + 12
        hotspots += 1 / (1 + math.exp(exp_input))

    return HotspotMetrics(
        change_count=num_of_changes,
        first_commit_datetime=first_commit_datetime,
        last_commit_datetime=last_commit_datetime,
        base_datetime=base_datetime_,
        hotspot=hotspots,
    )
