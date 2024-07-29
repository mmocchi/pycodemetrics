import datetime as dt


class GitFileCommitLog:
    def __init__(
        self,
        filepath: str,
        commit_hash: str,
        author: str,
        commit_date: dt.datetime,
        message: str,
    ):
        self.commit_hash = commit_hash
        self.filepath = filepath
        self.author = author
        self.commit_date = commit_date
        self.message = message

    def to_dict(self):
        """オブジェクトを辞書に変換する"""
        return {
            "commit_hash": self.commit_hash,
            "filepath": self.filepath,
            "author": self.author,
            "commit_date": self.commit_date,
            "message": self.message,
        }

    def __str__(self):
        """シンプルな文字列表現に変換する"""
        return f"{self.commit_hash},{self.filepath},{self.author},{self.commit_date},{self.message}"
