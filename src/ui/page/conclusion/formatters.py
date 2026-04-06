"""Scalar formatting helpers for the conclusion page."""
import datetime


def fmt_float(v) -> str:
    return f"{v:.2f}" if v is not None else '-'


def fmt_percent(v) -> str:
    return f"{v:.1f}%" if v is not None else '-'


def fmt_display(v) -> str:
    return str(v) if v is not None else '-'


def parse_year(date_str: str | None) -> int:
    if date_str:
        try:
            return 2000 + int(str(date_str)[:2])
        except (ValueError, TypeError):
            pass
    return datetime.date.today().year
