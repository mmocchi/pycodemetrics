import datetime as dt
import math
from typing import Self

from pydantic import BaseModel, computed_field, model_validator

from pycodemetrics.gitclient.models import GitFileCommitLog


class HotspotMetrics(BaseModel, frozen=True):
    change_count: int
    first_commit_datetime: dt.datetime
    last_commit_datetime: dt.datetime
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
        return (self.last_commit_datetime - self.first_commit_datetime).days

    def to_dict(self) -> dict:
        return self.model_dump()


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

    print(base_datetime_, last_commit_datetime)
    print((base_datetime_ - last_commit_datetime).total_seconds())

    hotspots = 0
    for log in gitlogs:
        t = 1 - (
            (last_commit_datetime - log.commit_date).total_seconds()
            / (last_commit_datetime - first_commit_datetime).total_seconds()
        )

        exp_input = (-12 * t) + 12
        hotspots += 1 / (1 + math.exp(exp_input))

    return HotspotMetrics(
        change_count=num_of_changes,
        first_commit_datetime=first_commit_datetime,
        last_commit_datetime=last_commit_datetime,
        hotspot=hotspots,
    )
