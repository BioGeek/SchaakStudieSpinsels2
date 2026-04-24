"""Locate and extract individual endgame studies from the book PDF.

Supersedes the study-boundary logic in scripts/pdf_processing.py, which
takes only the first `- N -` header in the top half of each page and
therefore silently drops studies that share a page with another (e.g.
study #8 on p46).

Algorithm:
  1. Walk every page and collect every span matching the `- N -` header.
     Record (page, column, y, number) for each.
  2. Sort headers in reading order: by (page, column, y) — left column
     top-to-bottom, then right column top-to-bottom.
  3. Each study runs from its header to the next header's position
     (possibly on the same page, possibly mid-column).

Usage:
    # List every study and its location
    uv run python scripts/study_extractor.py --list

    # Extract a specific study (plain text + diagram PNG) to a dir
    uv run python scripts/study_extractor.py --study 1 --out data/exemplar/1
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PDF = ROOT / "data" / "schaakstudiespinsels2.pdf"

# Chapter starts (0-based page index where the chapter title page sits).
# Matches scripts/pdf_processing.py::create_directory_structure TOC.
CHAPTERS: list[tuple[int, str, int]] = [
    (1, "Manke Maljutka's", 34),
    (2, "Maljutka's", 66),
    (3, "Mini - Studies", 120),
    (4, "Miniaturen", 206),
    (5, "Bijna - Miniaturen", 294),
    (6, "Studies", 354),
]

HEADER_RE = re.compile(r"^\s*-\s*(\d+)\s*-\s*$")


@dataclass
class StudyHeader:
    """Location of a `- N -` header inside the PDF."""

    number: int
    page: int       # 0-based page index
    column: int     # 0 = left, 1 = right
    y: float        # top-of-span y-coordinate inside the page
    x0: float       # left edge of the span's bounding box
    x1: float       # right edge of the span's bounding box

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class StudyRegion:
    """Start + end position for a study, across one or more columns."""

    number: int
    chapter_num: int
    chapter_name: str
    start_page: int
    start_column: int
    start_y: float
    # End is exclusive: the next header's position (or end-of-chapter).
    end_page: int
    end_column: int
    end_y: float

    def as_dict(self) -> dict:
        return asdict(self)


def column_of(span_x0: float, page_width: float) -> int:
    """Decide whether a span sits in the left (0) or right (1) column."""
    return 0 if span_x0 < page_width / 2 else 1


def find_study_headers(doc: pymupdf.Document) -> list[StudyHeader]:
    """Scan every page for `- N -` headers. Returns them in (page, col, y) order."""
    headers: list[StudyHeader] = []
    for page_idx, page in enumerate(doc):
        page_width = page.rect.width
        text_dict = page.get_text("dict")
        for block in text_dict.get("blocks", []):
            for line in block.get("lines", []):
                # Combine all spans on the line — a header may be split across spans.
                line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                m = HEADER_RE.match(line_text)
                if not m:
                    continue
                bbox = line.get("bbox") or (0, 0, 0, 0)
                x0, y0, x1, y1 = bbox
                headers.append(
                    StudyHeader(
                        number=int(m.group(1)),
                        page=page_idx,
                        column=column_of(x0, page_width),
                        y=y0,
                        x0=x0,
                        x1=x1,
                    )
                )
    headers.sort(key=lambda h: (h.page, h.column, h.y))
    return headers


def chapter_for(page: int) -> tuple[int, str]:
    """Return (chapter_num, chapter_name) for a given 0-based page index."""
    selected = (0, "(front matter)")
    for num, name, start_page in CHAPTERS:
        if page >= start_page:
            selected = (num, name)
        else:
            break
    return selected


def build_regions(headers: list[StudyHeader], doc: pymupdf.Document) -> list[StudyRegion]:
    """Pair each header with the next header's position to define the study's region."""
    regions: list[StudyRegion] = []
    end_of_doc = (len(doc) - 1, 1, 1e9)  # sentinel past the last page

    for i, h in enumerate(headers):
        end = headers[i + 1] if i + 1 < len(headers) else None
        if end is None:
            end_page, end_col, end_y = end_of_doc
        else:
            end_page, end_col, end_y = end.page, end.column, end.y
        chap_num, chap_name = chapter_for(h.page)
        regions.append(
            StudyRegion(
                number=h.number,
                chapter_num=chap_num,
                chapter_name=chap_name,
                start_page=h.page,
                start_column=h.column,
                start_y=h.y,
                end_page=end_page,
                end_column=end_col,
                end_y=end_y,
            )
        )
    return regions


def extract_region_text(doc: pymupdf.Document, region: StudyRegion) -> str:
    """Extract the plain text spanning the study's region, respecting columns.

    Walks each (page, column) between start and end in reading order and
    pulls text inside the clip rectangle. Returns newline-joined text.
    """
    chunks: list[str] = []

    def clip_for(page_idx: int, column: int, y0: float, y1: float) -> pymupdf.Rect:
        page = doc[page_idx]
        w = page.rect.width
        h = page.rect.height
        x_left = 0.0 if column == 0 else w / 2
        x_right = w / 2 if column == 0 else w
        return pymupdf.Rect(x_left, max(0.0, y0), x_right, min(h, y1))

    # Walk in reading order: (page, column) pairs between (start_page, start_col)
    # and (end_page, end_col) inclusive; within each, take the appropriate y-slice.
    p = region.start_page
    col = region.start_column

    def _next(p: int, col: int) -> tuple[int, int]:
        return (p, 1) if col == 0 else (p + 1, 0)

    while (p, col) <= (region.end_page, region.end_column):
        page = doc[p]
        y0 = region.start_y if (p, col) == (region.start_page, region.start_column) else 0.0
        y1 = region.end_y if (p, col) == (region.end_page, region.end_column) else page.rect.height
        if y1 <= y0:
            break
        clip = clip_for(p, col, y0, y1)
        chunks.append(page.get_text("text", clip=clip, sort=True))
        if (p, col) == (region.end_page, region.end_column):
            break
        p, col = _next(p, col)
        if p >= len(doc):
            break

    return "\n".join(chunks).strip()


def list_studies(pdf_path: Path) -> list[StudyRegion]:
    doc = pymupdf.open(pdf_path)
    try:
        headers = find_study_headers(doc)
        return build_regions(headers, doc)
    finally:
        doc.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    ap.add_argument("--list", action="store_true", help="list every study + location and exit")
    ap.add_argument("--study", type=int, help="study number to extract")
    ap.add_argument("--out", type=Path, help="output directory for --study")
    args = ap.parse_args()

    regions = list_studies(args.pdf)

    if args.list:
        print(f"{'num':>4} {'chap':>4} {'page':>5} {'col':>3} {'y0':>6}  -> "
              f"{'page':>5} {'col':>3} {'y1':>6}   chapter")
        for r in regions:
            print(
                f"{r.number:>4} {r.chapter_num:>4} {r.start_page:>5} {r.start_column:>3} "
                f"{r.start_y:>6.1f}  -> {r.end_page:>5} {r.end_column:>3} "
                f"{r.end_y:>6.1f}   {r.chapter_name}"
            )
        print(f"\nTotal: {len(regions)} studies found")
        return

    if args.study is None or args.out is None:
        ap.error("--list, or both --study and --out, required")

    target = next((r for r in regions if r.number == args.study), None)
    if target is None:
        raise SystemExit(f"study #{args.study} not found")

    args.out.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(args.pdf)
    try:
        text = extract_region_text(doc, target)
        (args.out / "region.json").write_text(
            json.dumps(target.as_dict(), indent=2), encoding="utf-8"
        )
        (args.out / "text.txt").write_text(text, encoding="utf-8")

        # Render the start-of-study area as a PNG so we can eyeball the
        # diagram and derive the starting FEN manually (the book's own
        # piece-classification pipeline is not yet trustworthy). Width:
        # the start column; height: from the header down to the next
        # header or a generous default.
        page = doc[target.start_page]
        w = page.rect.width
        x_left = 0.0 if target.start_column == 0 else w / 2
        x_right = w / 2 if target.start_column == 0 else w
        y_top = target.start_y
        y_bot = (
            target.end_y
            if target.end_page == target.start_page and target.end_column == target.start_column
            else min(y_top + 400, page.rect.height)
        )
        clip = pymupdf.Rect(x_left, y_top, x_right, y_bot)
        pix = page.get_pixmap(clip=clip, matrix=pymupdf.Matrix(3, 3))
        pix.save(str(args.out / "diagram_region.png"))
        print(
            f"wrote {args.out}/region.json, text.txt ({len(text)} chars), "
            f"and diagram_region.png"
        )
    finally:
        doc.close()


if __name__ == "__main__":
    main()
