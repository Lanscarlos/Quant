"""Scalar formatting helpers shared across detail sub-pages."""
import datetime


def _f(v) -> str:
    return f"{v:.2f}" if v is not None else '-'


def _p(v) -> str:
    return f"{v:.1f}%" if v is not None else '-'


def _d(v) -> str:
    return str(v) if v is not None else '-'


def _parse_year(date_str: str | None) -> int:
    if date_str:
        try:
            return 2000 + int(str(date_str)[:2])
        except (ValueError, TypeError):
            pass
    return datetime.date.today().year