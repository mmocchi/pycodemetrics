import datetime as dt
from typing import Self

from pydantic import BaseModel, computed_field, model_validator

from pycodemetrics.gitclient.models import GitFileCommitLog


class HotspotMetrics(BaseModel, frozen=True):
    change_count: int
    first_commit_datetime: dt.datetime
    last_commit_datetime: dt.datetime

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

    @computed_field(return_type=float)  # type: ignore
    @property
    def hotspot(self):
        if self.lifetime_days == 0:
            return 0

        return self.change_count / self.lifetime_days

    def to_dict(self) -> dict:
        return self.model_dump()


def calculate_hotspot(gitlogs: list[GitFileCommitLog]) -> HotspotMetrics:
    """
    Calculate the hotspot metric.

    Args:
        gitlogs (list[GitFileCommitLog]): A list of GitFileCommitLog.

    Returns:
        float: The hotspot metric.
    """

    first_commit_datetime = min([log.commit_date for log in gitlogs])
    last_commit_datetime = max([log.commit_date for log in gitlogs])

    num_of_changes = len(gitlogs)

    return HotspotMetrics(
        change_count=num_of_changes,
        first_commit_datetime=first_commit_datetime,
        last_commit_datetime=last_commit_datetime,
    )
