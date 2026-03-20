from __future__ import annotations

import pandas as pd


def make_slice_id(date: pd.Timestamp, freq: str) -> str:
    if freq == "yearly":
        return f"{date.year}"
    if freq == "semester":
        semester = 1 if date.month <= 6 else 2
        return f"{date.year}S{semester}"
    raise ValueError(f"Unsupported frequency: {freq}")


def slice_sort_key(slice_id: str) -> tuple[int, int]:
    if "S" in slice_id:
        year_str, semester_str = slice_id.split("S", maxsplit=1)
        return (int(year_str), int(semester_str))
    return (int(slice_id), 0)
