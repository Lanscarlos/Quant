"""Convert docs/database_schema.md to docs/database_schema.pdf with Chinese support."""
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

# ── Fonts ──────────────────────────────────────────────────────────────────────
_FONT_DIR = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("MSYH",     str(_FONT_DIR / "msyh.ttc"),   subfontIndex=0))
pdfmetrics.registerFont(TTFont("MSYHBold", str(_FONT_DIR / "msyhbd.ttc"), subfontIndex=0))
pdfmetrics.registerFontFamily("MSYH", normal="MSYH", bold="MSYHBold")

# ── Palette ────────────────────────────────────────────────────────────────────
C_NAVY      = colors.HexColor("#1a3a5c")
C_BLUE      = colors.HexColor("#2d6a9f")
C_BLUE_LITE = colors.HexColor("#dbeafe")
C_STRIPE    = colors.HexColor("#f4f7fb")
C_BORDER    = colors.HexColor("#cfd8e3")
C_CODE_BG   = colors.HexColor("#f1f3f5")
C_CODE_FG   = colors.HexColor("#c0392b")

# ── Styles ─────────────────────────────────────────────────────────────────────
def _s(name, **kw):
    kw.setdefault("fontName", "MSYH")
    kw.setdefault("fontSize", 10)
    kw.setdefault("leading",  16)
    kw.setdefault("alignment", TA_LEFT)
    return ParagraphStyle(name, **kw)

S = {
    "h1":  _s("h1",  fontName="MSYHBold", fontSize=20, leading=28,
               textColor=C_NAVY, spaceAfter=10, spaceBefore=4),
    "h2":  _s("h2",  fontName="MSYHBold", fontSize=14, leading=20,
               textColor=C_BLUE, spaceAfter=6, spaceBefore=14),
    "h3":  _s("h3",  fontName="MSYHBold", fontSize=11, leading=16,
               textColor=C_NAVY, spaceAfter=4, spaceBefore=10),
    "body": _s("body", spaceAfter=4, leading=17),
    "bq":   _s("bq",  fontSize=9, leading=14, leftIndent=8,
                textColor=colors.HexColor("#444444")),
    "code": _s("code", fontName="Courier", fontSize=8, leading=12,
                textColor=colors.HexColor("#1e1e1e")),
    "th":   _s("th",  fontName="MSYHBold", fontSize=9, leading=13,
                textColor=colors.white),
    "td":   _s("td",  fontSize=9, leading=13),
}

# ── Inline markdown → reportlab XML ───────────────────────────────────────────
def _inline(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`",
                  rf'<font name="Courier" color="{C_CODE_FG.hexval()}">\1</font>', text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    return text

# ── Table builder ──────────────────────────────────────────────────────────────
_PW = 16.5 * cm   # usable page width

def _col_widths(n: int):
    if n == 4:
        return [3.0*cm, 2.2*cm, 1.8*cm, _PW - 7.0*cm]
    if n == 3:
        return [3.5*cm, 3.0*cm, _PW - 6.5*cm]
    if n == 2:
        return [4.5*cm, _PW - 4.5*cm]
    return [_PW / n] * n

def _cell(text: str, header: bool = False) -> Paragraph:
    return Paragraph(_inline(text.strip()), S["th"] if header else S["td"])

def _build_md_table(lines: list[str]):
    rows = []
    for ln in lines:
        if re.match(r"^\|[-| :]+\|$", ln.strip()):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        rows.append(cells)
    if not rows:
        return Spacer(1, 1)

    ncols = len(rows[0])
    cw    = _col_widths(ncols)
    data  = [[_cell(c, header=True) for c in rows[0]]]
    for row in rows[1:]:
        while len(row) < ncols:
            row.append("")
        data.append([_cell(c) for c in row[:ncols]])

    tbl = Table(data, colWidths=cw, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1,  0), C_BLUE),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, C_STRIPE]),
        ("GRID",          (0, 0), (-1, -1), 0.5, C_BORDER),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    return tbl

def _code_block(lines: list[str]):
    raw = "\n".join(lines)
    escaped = raw.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    markup  = escaped.replace("\n", "<br/>")
    inner   = Paragraph(markup, S["code"])
    tbl = Table([[inner]], colWidths=[_PW])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_CODE_BG),
        ("BOX",           (0, 0), (-1, -1), 0.5, C_BORDER),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return tbl

# ── Main parser ────────────────────────────────────────────────────────────────
def parse(md: str) -> list:
    out    = []
    lines  = md.splitlines()
    i      = 0

    while i < len(lines):
        ln = lines[i]

        # Fenced code block
        if ln.strip().startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            out.append(Spacer(1, 4))
            out.append(_code_block(code))
            out.append(Spacer(1, 4))
            i += 1
            continue

        # H1
        if re.match(r"^# [^#]", ln):
            out.append(Paragraph(_inline(ln[2:]), S["h1"]))
            i += 1; continue

        # H2
        if re.match(r"^## [^#]", ln):
            out.append(Spacer(1, 4))
            out.append(HRFlowable(width="100%", thickness=1.5,
                                   color=C_BLUE, spaceAfter=2))
            out.append(Paragraph(_inline(ln[3:]), S["h2"]))
            i += 1; continue

        # H3
        if re.match(r"^### ", ln):
            out.append(Paragraph(_inline(ln[4:]), S["h3"]))
            i += 1; continue

        # HR
        if ln.strip() == "---":
            out.append(HRFlowable(width="100%", thickness=0.5,
                                   color=C_BORDER, spaceBefore=2, spaceAfter=2))
            i += 1; continue

        # Blockquote
        if ln.startswith("> "):
            bq = []
            while i < len(lines) and lines[i].startswith("> "):
                bq.append(lines[i][2:])
                i += 1
            inner = Paragraph(_inline(" ".join(bq)), S["bq"])
            tbl   = Table([[inner]], colWidths=[_PW])
            tbl.setStyle(TableStyle([
                ("BACKGROUND",   (0, 0), (-1, -1), colors.HexColor("#eef2f7")),
                ("LINEBEFORE",   (0, 0), (0, -1),  3, C_BLUE),
                ("LEFTPADDING",  (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING",   (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
            ]))
            out.append(tbl)
            out.append(Spacer(1, 4))
            continue

        # Markdown table
        if ln.startswith("|"):
            tbl_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                tbl_lines.append(lines[i])
                i += 1
            out.append(_build_md_table(tbl_lines))
            out.append(Spacer(1, 6))
            continue

        # Bullet list
        if ln.startswith("- "):
            while i < len(lines) and lines[i].startswith("- "):
                out.append(Paragraph("• " + _inline(lines[i][2:]), S["body"]))
                i += 1
            continue

        # Empty line
        if not ln.strip():
            out.append(Spacer(1, 4))
            i += 1; continue

        # Plain paragraph (collect continuation lines)
        buf = []
        while (i < len(lines) and lines[i].strip()
               and not re.match(r"^#{1,3} ", lines[i])
               and not lines[i].startswith("|")
               and not lines[i].startswith("```")
               and not lines[i].startswith("> ")
               and not lines[i].startswith("- ")
               and lines[i].strip() != "---"):
            buf.append(lines[i])
            i += 1
        if buf:
            out.append(Paragraph(_inline(" ".join(buf)), S["body"]))

    return out


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    md_path  = Path("docs/数据库说明.md")
    out_path = Path("docs/数据库说明.pdf")

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.0*cm,
        topMargin=2.5*cm,  bottomMargin=2.0*cm,
        title="Database Schema — Quant",
        author="Quant",
    )
    doc.build(parse(md_path.read_text(encoding="utf-8")))
    print(f"Done: {out_path}")


if __name__ == "__main__":
    main()