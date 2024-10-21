import datetime as dt
from pathlib import Path

from pydantic import BaseModel


class GitFileCommitLog(BaseModel, frozen=True, extra="forbid"):
    """
    Git file commit log.

    filepath (Path): The path to the file.
    commit_hash (str): The commit hash.
    author (str): The author of the commit.
    commit_date (dt.datetime): The commit date.
    message (str): The commit message.
    """

    filepath: Path
    commit_hash: str
    author: str
    commit_date: dt.datetime
    message: str

    def __str__(self) -> str:
        """シンプルな文字列表現に変換する"""
        return f"{self.commit_hash},{self.filepath},{self.author},{self.commit_date},{self.message}"
