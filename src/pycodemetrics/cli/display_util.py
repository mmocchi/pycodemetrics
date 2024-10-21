from enum import Enum

import pandas as pd
import tabulate


class DisplayFormat(str, Enum):
    """
    Display format for the result.

    TABLE: Display the result as a table.
    CSV: Display the result as a CSV format.
    JSON: Display the result as a JSON format.
    """

    TABLE = "table"
    CSV = "csv"
    JSON = "json"

    @classmethod
    def to_list(cls) -> list[str]:
        """
        Get the list of display formats.

        Returns:
            list[str]: List of display format values.
        """
        return [e.value for e in cls]


def head_for_display(results_df: pd.DataFrame, limit: int | None) -> pd.DataFrame:
    """
    Limit the number of files to display from the result of analyze_hotspot_metrics

    Args:
        results_df (pd.DataFrame): Result of analyze_hotspot_metrics.
        limit (int | None): Limit the number of files to display. If None, display all files.

    Returns:
        pd.DataFrame: Limited result for display.
    """
    if limit is None:
        return results_df

    if limit < 0:
        raise ValueError(f"Invalid limit: {limit}")
    return results_df.head(limit)


def display(results_df: pd.DataFrame, display_format: DisplayFormat) -> None:
    """
    Display the result.

    Args:
        results_df (pd.DataFrame): The result as a DataFrame.
        display_format (DisplayFormat): Display format for the result.

    """
    if display_format == DisplayFormat.TABLE:
        result_table = tabulate.tabulate(results_df, headers="keys")  # type: ignore
        print(result_table)
    elif display_format == DisplayFormat.CSV:
        print(results_df.to_csv(index=False))
    elif display_format == DisplayFormat.JSON:
        print(
            results_df.to_json(
                orient="records", indent=2, force_ascii=False, default_handler=str
            )
        )
    else:
        raise ValueError(f"Invalid display format: {display_format}")
