#!/usr/bin/env python3
"""
Maison BU PDF Exporter
Converts campaign .txt output files to styled, branded PDFs.
"""
from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

# Liberation font paths (bundled with most Linux distributions)
_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-{}.ttf"
_SANS  = "/usr/share/fonts/truetype/liberation/LiberationSans-{}.ttf"

OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"
PDF_DIR     = OUTPUTS_DIR / "pdf"

# Brand palette — RGB tuples matching HTML email
C_DARK    = (26,  26,  24)   # #1A1A18 deep near-black
C_BODY    = (42,  42,  40)   # #2A2A28 body text
C_GRAY    = (136, 130, 122)  # mid gray for labels
C_LGRAY   = (187, 187, 187)  # #BBB footer text
C_DIVIDER = (201, 191, 180)  # #C9BFB4 thin rules
C_SECTION = (237, 233, 227)  # #EDE9E3 section background

PW, PH   = 210, 297          # A4 dimensions in mm
ML, MR   = 20,  20           # left / right margins
CW       = PW - ML - MR      # content width = 170 mm


# ── branded FPDF subclass ─────────────────────────────────────────────

class _PDF(FPDF):
    def __init__(self, doc_title: str, doc_subtitle: str) -> None:
        super().__init__("P", "mm", "A4")
        self._doc_title    = doc_title
        self._doc_subtitle = doc_subtitle
        self._ready        = False

    def _load(self) -> None:
        if self._ready:
            return
        for variant, style in [
            ("Regular", ""), ("Bold", "B"),
            ("Italic", "I"), ("BoldItalic", "BI"),
        ]:
            self.add_font("Serif", style, _SERIF.format(variant))
        self.add_font("Sans", "",  _SANS.format("Regular"))
        self.add_font("Sans", "B", _SANS.format("Bold"))
        self._ready = True

    def header(self) -> None:
        self._load()
        if self.page_no() == 1:
            # Top accent bar only on first page
            self.set_fill_color(*C_DARK)
            self.rect(0, 0, PW, 3, "F")
            return
        # Running header: wordmark left, page number right
        self.set_y(7)
        self.set_font("Sans", "", 7.5)
        self.set_text_color(*C_GRAY)
        self.set_x(ML)
        self.cell(CW, 5, "MAISON BU  ·  HASSELT", align="L")
        self.set_x(ML)
        self.cell(CW, 5, str(self.page_no()), align="R")
        self.set_draw_color(*C_DIVIDER)
        self.line(ML, 14, PW - MR, 14)
        self.set_y(18)

    def footer(self) -> None:
        self._load()
        self.set_y(-16)
        self.set_draw_color(*C_DIVIDER)
        self.line(ML, self.get_y(), PW - MR, self.get_y())
        self.ln(2)
        self.set_font("Sans", "", 7.5)
        self.set_text_color(*C_LGRAY)
        self.set_x(ML)
        self.cell(CW, 4, "Maison BU  ·  Hasselt  ·  België", align="C")
        # Bottom accent bar
        self.set_fill_color(*C_DARK)
        self.rect(0, PH - 3, PW, 3, "F")


# ── parser ────────────────────────────────────────────────────────────

def _parse(text: str) -> tuple[dict, list[tuple[str, str]]]:
    """
    Parse a .txt campaign file into (header_info, elements).

    Element types:
      section_header   — ╔═══║═══╚ block
      subsection_header — ━━━/title/━━━ block
      rule             — ─────── thin horizontal
      body             — regular text line (may be indented)
      hashtags         — line starting with # containing multiple tags
      empty            — blank line
    """
    lines = text.splitlines()
    info  = {"title": "", "subtitle": "", "agent": ""}
    elems: list[tuple[str, str]] = []
    i = 0

    # Skip leading blank lines
    while i < len(lines) and not lines[i].strip():
        i += 1

    # File header block: ─── / lines / ───
    if i < len(lines) and _is_thin(lines[i].strip()):
        i += 1
        hlines: list[str] = []
        while i < len(lines) and not _is_thin(lines[i].strip()):
            if lines[i].strip():
                hlines.append(lines[i].strip())
            i += 1
        i += 1  # closing rule
        info["title"]    = hlines[0] if len(hlines) > 0 else ""
        info["subtitle"] = hlines[1] if len(hlines) > 1 else ""
        info["agent"]    = hlines[2] if len(hlines) > 2 else ""

    # Content body
    while i < len(lines):
        line     = lines[i]
        stripped = line.strip()

        if not stripped:
            elems.append(("empty", ""))
            i += 1
            continue

        # Section header: ╔═══╗ … ║ … ╚═══╝
        if stripped.startswith("╔"):
            titles: list[str] = []
            i += 1
            while i < len(lines):
                s = lines[i].strip()
                if s.startswith("╚"):   # ╚
                    i += 1
                    break
                if s.startswith("║"):   # ║
                    c = s.strip("║").strip()
                    if c:
                        titles.append(c)
                i += 1
            if titles:
                elems.append(("section_header", "\n".join(titles)))
            continue

        # Subsection divider: ━━━━━
        if _is_thick(stripped):
            title_lines: list[str] = []
            i += 1
            while i < len(lines):
                s = lines[i].strip()
                if _is_thick(s) or s.startswith("╔"):
                    if _is_thick(s):
                        i += 1
                    break
                if s:
                    title_lines.append(s)
                else:
                    break
                i += 1
            if title_lines:
                elems.append(("subsection_header", "\n".join(title_lines)))
            continue

        # Thin horizontal rule: ─────
        if _is_thin(stripped):
            elems.append(("rule", ""))
            i += 1
            continue

        # Hashtag line
        if stripped.startswith("#") and stripped.count("#") >= 2:
            elems.append(("hashtags", stripped))
            i += 1
            continue

        elems.append(("body", line.rstrip()))
        i += 1

    return info, elems


_GLYPH_SUBS = str.maketrans(
    {"✓": "[v]", "✗": "[x]", "☐": "[ ]", "☑": "[v]", "★": "*", "·": "·"}
)


def _clean(text: str) -> str:
    return text.translate(_GLYPH_SUBS)


def _is_thin(s: str) -> bool:
    return bool(s) and all(c in "─═" for c in s) and len(s) > 8


def _is_thick(s: str) -> bool:
    return bool(s) and all(c == "━" for c in s) and len(s) > 5


# ── renderer ──────────────────────────────────────────────────────────

def _render(pdf: _PDF, info: dict, elems: list[tuple[str, str]]) -> None:
    pdf.set_margins(ML, 18, MR)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf._load()

    # ── First-page title block ────────────────────────────────────────
    pdf.set_y(10)
    pdf.set_font("Sans", "", 8)
    pdf.set_text_color(*C_GRAY)
    pdf.set_x(ML)
    pdf.cell(CW, 6, "M A I S O N   B U   ·   H A S S E L T", align="C")

    divider_y = pdf.get_y() + 3
    pdf.set_draw_color(*C_DIVIDER)
    pdf.line(ML + 35, divider_y, PW - MR - 35, divider_y)
    pdf.set_y(divider_y + 5)

    if info["title"]:
        pdf.set_font("Serif", "I", 18)
        pdf.set_text_color(*C_DARK)
        pdf.set_x(ML)
        pdf.multi_cell(CW, 9, _clean(info["title"]), align="C")
        pdf.ln(2)

    if info["subtitle"]:
        pdf.set_font("Serif", "", 11)
        pdf.set_text_color(*C_BODY)
        pdf.set_x(ML)
        pdf.multi_cell(CW, 6, _clean(info["subtitle"]), align="C")

    if info["agent"]:
        pdf.ln(1)
        pdf.set_font("Sans", "", 8.5)
        pdf.set_text_color(*C_GRAY)
        pdf.set_x(ML)
        pdf.multi_cell(CW, 5, _clean(info["agent"]), align="C")

    pdf.ln(7)
    pdf.set_draw_color(*C_DIVIDER)
    pdf.line(ML, pdf.get_y(), PW - MR, pdf.get_y())
    pdf.ln(7)

    # ── Content elements ──────────────────────────────────────────────
    for elem_type, content in elems:

        if elem_type == "empty":
            pdf.ln(3)

        elif elem_type == "rule":
            pdf.ln(2)
            pdf.set_draw_color(*C_DIVIDER)
            pdf.line(ML, pdf.get_y(), PW - MR, pdf.get_y())
            pdf.ln(4)

        elif elem_type == "section_header":
            pdf.ln(3)
            hlines  = content.split("\n")
            box_h   = 5 + len(hlines) * 6.5 + 4
            if pdf.get_y() + box_h > PH - 22:
                pdf.add_page()
                pdf.ln(2)
            y0 = pdf.get_y()
            pdf.set_fill_color(*C_SECTION)
            pdf.rect(ML - 2, y0, CW + 4, box_h, "F")
            pdf.set_y(y0 + 5)
            for j, hline in enumerate(hlines):
                if j == 0:
                    pdf.set_font("Serif", "B", 12)
                    pdf.set_text_color(*C_DARK)
                else:
                    pdf.set_font("Sans", "", 9)
                    pdf.set_text_color(*C_GRAY)
                pdf.set_x(ML)
                pdf.multi_cell(CW, 6.5, _clean(hline), align="L")
            pdf.set_y(y0 + box_h + 4)

        elif elem_type == "subsection_header":
            pdf.ln(4)
            pdf.set_draw_color(*C_DIVIDER)
            pdf.line(ML, pdf.get_y(), PW - MR, pdf.get_y())
            pdf.ln(3)
            slines = content.split("\n")
            for j, sline in enumerate(slines):
                if j == 0:
                    pdf.set_font("Serif", "B", 10.5)
                    pdf.set_text_color(*C_DARK)
                else:
                    pdf.set_font("Sans", "", 8.5)
                    pdf.set_text_color(*C_GRAY)
                pdf.set_x(ML)
                pdf.multi_cell(CW, 5.5, _clean(sline), align="L")
            pdf.ln(3)

        elif elem_type == "body":
            n_spaces = len(content) - len(content.lstrip())
            text     = content.lstrip()
            if not text:
                continue
            indent = min(n_spaces * 1.5, 14.0)  # leading spaces → mm, capped at 14
            pdf.set_font("Serif", "", 10.5)
            pdf.set_text_color(*C_BODY)
            pdf.set_x(ML + indent)
            pdf.multi_cell(CW - indent, 5.5, _clean(text), align="L")

        elif elem_type == "hashtags":
            pdf.ln(1)
            pdf.set_font("Sans", "", 8)
            pdf.set_text_color(*C_LGRAY)
            pdf.set_x(ML)
            pdf.multi_cell(CW, 4.5, _clean(content), align="L")
            pdf.ln(2)


# ── public API ────────────────────────────────────────────────────────

class MaisonBUPdfExporter:
    """Convert Maison BU .txt campaign files to branded PDFs."""

    def export_file(self, txt_path: "Path | str") -> Path:
        """Export a single .txt file. Returns the output PDF path."""
        txt_path = Path(txt_path)
        if not txt_path.exists():
            raise FileNotFoundError(f"Bestand niet gevonden: {txt_path}")
        info, elems = _parse(txt_path.read_text(encoding="utf-8"))
        pdf = _PDF(info["title"], info["subtitle"])
        _render(pdf, info, elems)
        PDF_DIR.mkdir(parents=True, exist_ok=True)
        out = PDF_DIR / (txt_path.stem + ".pdf")
        pdf.output(str(out))
        return out

    def export_all(self) -> list[Path]:
        """Export every .txt file under outputs/ (skips outputs/pdf/)."""
        paths = sorted(
            p for p in OUTPUTS_DIR.rglob("*.txt") if "pdf" not in p.parts
        )
        return [self.export_file(p) for p in paths]

    def export_campaign(self, keyword: str) -> list[Path]:
        """Export all .txt files whose filename contains *keyword*."""
        paths = sorted(
            p for p in OUTPUTS_DIR.rglob("*.txt")
            if keyword.lower() in p.name.lower() and "pdf" not in p.parts
        )
        return [self.export_file(p) for p in paths]
