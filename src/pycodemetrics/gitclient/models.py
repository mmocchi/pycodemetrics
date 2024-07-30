import datetime as dt

from pydantic import BaseModel


class GitFileCommitLog(BaseModel, frozen=True):
    filepath: str
    commit_hash: str
    author: str
    commit_date: dt.datetime
    message: str

    def __str__(self):
        """シンプルな文字列表現に変換する"""
        return f"{self.commit_hash},{self.filepath},{self.author},{self.commit_date},{self.message}"
