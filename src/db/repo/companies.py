"""
Repository: companies

Writes betting company dictionary records from match_odds results.
Strategy: INSERT OR IGNORE — company metadata is written once and never overwritten.
"""
import sqlite3


def upsert_companies(conn: sqlite3.Connection, records: list[dict]) -> int:
    """Insert company rows extracted from match_odds_list records.

    Each dict must contain: company_id, company_name, and optionally label.
    Skips records with missing or invalid company_id.
    Returns the number of unique company rows inserted.
    """
    seen: set[int] = set()
    rows: list[tuple] = []

    for r in records:
        cid = _int(r.get("company_id"))
        name = (r.get("company_name") or "").strip()
        if not cid or not name or cid in seen:
            continue
        seen.add(cid)
        rows.append((
            cid,
            name,
            r.get("label") or None,
        ))

    if not rows:
        return 0

    with conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO companies (company_id, company_name, label)
            VALUES (?, ?, ?)
            """,
            rows,
        )
    return len(rows)


def _int(val) -> int | None:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None