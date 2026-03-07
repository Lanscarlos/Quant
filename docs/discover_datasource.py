"""
Given a match_list page URL (e.g. https://live.titan007.com/oldIndexall.aspx),
trace the actual data source JS file URL for today's match data.

Steps:
  1. Fetch the HTML page — search for bfdata <script> tags directly
  2. Find func.js <script> tag → fetch it
  3. Extract LoadLiveFile() with balanced-brace parsing
  4. Show all URL-like strings near "bfdata" / "VbsXml"
  5. Verify each candidate URL (fetch + check matchdate field)
"""
import re
import sys
from urllib.parse import urljoin

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}


# ---------------------------------------------------------------------------
# Network helpers
# ---------------------------------------------------------------------------

def fetch(url: str, encoding: str = "gbk", referer: str = "") -> str:
    hdrs = {**HEADERS, "Referer": referer or url}
    resp = requests.get(url, headers=hdrs, timeout=15)
    resp.raise_for_status()
    return resp.content.decode(encoding, errors="replace")


def abs_url(src: str, base: str) -> str:
    """Resolve src (possibly protocol-relative) against base."""
    if src.startswith("//"):
        src = "https:" + src
    return urljoin(base, src)


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def find_script_urls(html: str, base_url: str, filename: str) -> list[str]:
    """Return all absolute URLs of <script src="...filename..."> tags."""
    pattern = rf'<script[^>]+src=["\']?([^"\'>\s]*{re.escape(filename)}[^"\'>\s]*)'
    return [abs_url(m.group(1), base_url) for m in re.finditer(pattern, html, re.IGNORECASE)]


def extract_function(source: str, func_name: str) -> str | None:
    """Extract a function body using balanced-brace counting."""
    start = source.find(f"function {func_name}")
    if start == -1:
        return None
    brace_start = source.find("{", start)
    if brace_start == -1:
        return None
    depth = 0
    for i, ch in enumerate(source[brace_start:], brace_start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[start : i + 1]
    return None


def find_url_candidates(text: str) -> list[str]:
    """
    Find all URL-like string fragments in JS text.
    Includes:
      - Full quoted URLs containing bfdata/VbsXml
      - String concatenation fragments that contain bfdata/VbsXml
    """
    # Quoted strings with relevant keywords
    quoted = re.findall(r'["\']([^"\']{3,}(?:bfdata|VbsXml)[^"\']*)["\']', text)
    # Broader: any string literal within 200 chars of "bfdata"
    broad: list[str] = []
    for m in re.finditer(r'bfdata|VbsXml', text):
        ctx = text[max(0, m.start() - 200) : m.end() + 200]
        strings = re.findall(r'["\']([^"\']{5,})["\']', ctx)
        broad.extend(strings)
    return list(dict.fromkeys(quoted + broad))


def check_date(url: str, base_url: str) -> str:
    """Fetch url and return the matchdate value, or an error string."""
    try:
        js = fetch(abs_url(url, base_url), referer=base_url)
        m = re.search(r'var matchdate="([^"]+)"', js)
        if m:
            return m.group(1)
        # Try A[1] first row to infer date
        m2 = re.search(r'A\[1]="([^"]+)"', js)
        if m2:
            fields = m2.group(1).split("^")
            return f"(from A[1][11]={fields[11] if len(fields) > 11 else '?'})"
        return "(no matchdate found)"
    except Exception as e:
        return f"ERROR: {e}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(page_url: str):
    print(f"\n{'='*60}")
    print(f"Page: {page_url}")
    print(f"{'='*60}")

    # 1. Fetch HTML
    print("\n[1] Fetching HTML...")
    try:
        html = fetch(page_url, encoding="utf-8")
    except Exception as e:
        print(f"    ERROR: {e}")
        return

    # 2. Look for bfdata <script> tags directly in the HTML
    print("\n[2] Searching HTML for bfdata <script> tags...")
    bfdata_tags = find_script_urls(html, page_url, "bfdata")
    if bfdata_tags:
        for u in bfdata_tags:
            date = check_date(u, page_url)
            print(f"    FOUND: {u}  →  matchdate={date}")
    else:
        print("    (none)")

    # 3. Also grep HTML inline scripts for bfdata/VbsXml
    print("\n[3] Searching inline <script> blocks for bfdata/VbsXml...")
    inline_candidates = find_url_candidates(html)
    if inline_candidates:
        for c in inline_candidates:
            print(f"    {c!r}")
    else:
        print("    (none)")

    # 4. Find and fetch func.js
    func_urls = find_script_urls(html, page_url, "func.js")
    if not func_urls:
        print("\n[4] func.js not found in HTML")
        return

    func_url = func_urls[0]
    print(f"\n[4] Fetching func.js: {func_url}")
    try:
        func_js = fetch(func_url, referer=page_url)
    except Exception as e:
        print(f"    ERROR: {e}")
        return

    # 5. Extract LoadLiveFile() with balanced braces
    print("\n[5] Extracting LoadLiveFile()...")
    fn_body = extract_function(func_js, "LoadLiveFile")
    if fn_body:
        print(fn_body[:1200])
    else:
        print("    LoadLiveFile() not found in func.js")

    # 6. Find all bfdata/VbsXml URL candidates in func.js
    print("\n[6] URL candidates in func.js:")
    candidates = find_url_candidates(func_js)
    if candidates:
        for c in candidates:
            print(f"    {c!r}")
    else:
        print("    (none)")

    # 7. Verify each candidate
    print("\n[7] Verifying URL candidates (fetch + matchdate)...")
    for c in candidates:
        # Only try things that look like paths/URLs
        if "/" in c and len(c) > 5:
            date = check_date(c, page_url)
            print(f"    {c!r}  →  matchdate={date}")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://live.titan007.com/oldIndexall.aspx"
    main(url)