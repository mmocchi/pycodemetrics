from enum import Enum
from pathlib import Path

import pandas as pd


class ExportFormat(str, Enum):
    """
    Export format for analyze_hotspot_metrics

    Args:
        CSV: Export the result as a CSV.
        JSON: Export the result as a JSON.
    """

    CSV = "csv"
    JSON = "json"

    @classmethod
    def to_list(cls) -> list[str]:
        """
        Returns:
            list[str]: List of export format values.
        """
        return [e.value for e in cls]

    def get_ext(self) -> str:
        """
        Returns:
            str: File extension for the export format.
        """
        return f".{self.value}"


def export(
    results_df: pd.DataFrame,
    export_file_path: Path | None,
    overwrite: bool = False,
) -> None:
    """
    Export the result of analyze

    Args:
        results_df (pd.DataFrame): Result of analyze.
        export_file_path (Path): Export file path.
        overwrite (bool): Overwrite the export file if it already exists.
    """

    if export_file_path is None:
        raise ValueError("Export file path is not specified")

    if export_file_path.exists() and not overwrite:
        raise FileExistsError(
            f"{export_file_path} already exists. Use --overwrite option to overwrite the file"
        )

    export_file_path.parent.mkdir(parents=True, exist_ok=True)

    if export_file_path.suffix == ExportFormat.CSV.get_ext():
        results_df.to_csv(export_file_path, index=False)
    elif export_file_path.suffix == ExportFormat.JSON.get_ext():
        results_df.to_json(
            export_file_path, orient="records", indent=4, force_ascii=False
        )
    else:
        raise ValueError(f"Invalid export format: {export_file_path.suffix}")
