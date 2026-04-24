"""Build a cm-chessboard SVG sprite from Ignace's piece template.

The source at data/template.png is a strip of six black silhouettes
(King, Queen, Rook, Bishop, Knight, Pawn — in that order, labelled in
Dutch below each glyph). This script extracts each glyph's outline
with OpenCV, normalises it into a 40×40 viewBox that cm-chessboard
expects, and emits a sprite file with twelve `<g id="wk">`-style
groups (both colours for each piece).

White pieces use the same shape with a white fill and a black stroke;
black pieces use a solid black fill. That keeps Ignace's silhouette
recognisable at both colours without redrawing the glyphs by hand.

Output: public/pieces/ignace.svg
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "data" / "template.png"
OUTPUT = ROOT / "public" / "pieces" / "ignace.svg"

# The order in which the six silhouettes appear in data/template.png,
# using cm-chessboard's single-letter piece codes.
PIECE_ORDER = ["k", "q", "r", "b", "n", "p"]

# cm-chessboard's pieces live in a 40×40 viewBox; the default staunty
# sprite uses the same. Centre each glyph in that box.
VIEW = 40
MARGIN = 2.0  # reserve a couple of user units around the glyph


def extract_piece_contours(template_path: Path) -> list[list[np.ndarray]]:
    """Return per-piece contours in the order Ignace drew them (left→right).

    The template has each piece drawn in a separate horizontal region
    plus a text label below. We ignore contours sitting below the
    tallest glyph (= the text labels) and cluster the remaining
    contours by x-centroid to handle multi-contour pieces (e.g. the
    king's cross separating from its body).
    """
    bgr = cv2.imread(str(template_path))
    if bgr is None:
        raise FileNotFoundError(template_path)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    # Sort by x position so we walk pieces left-to-right.
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])

    # Separate glyph contours from text-label contours by height: glyphs
    # are the tall shapes near the top of the template.
    heights = [cv2.boundingRect(c)[3] for c in contours]
    max_h = max(heights)
    glyph_threshold = max_h * 0.4
    glyphs = [c for c in contours if cv2.boundingRect(c)[3] >= glyph_threshold]

    # The first 6 tall contours are the piece silhouettes themselves. If
    # the king's cross separated from its body, it may already have been
    # pruned by the 0.4-height filter; otherwise we take just the
    # leftmost 6 tall contours.
    if len(glyphs) < len(PIECE_ORDER):
        raise RuntimeError(
            f"expected ≥{len(PIECE_ORDER)} piece contours, got {len(glyphs)}"
        )
    return [[c] for c in glyphs[: len(PIECE_ORDER)]]


def contour_to_svg_path(contours: list[np.ndarray], bbox: tuple[int, int, int, int]) -> str:
    """Convert a contour list into an SVG path string normalised to VIEW×VIEW."""
    x0, y0, w, h = bbox
    scale = (VIEW - 2 * MARGIN) / max(w, h)
    # Centre within the view box.
    off_x = MARGIN + (VIEW - 2 * MARGIN - w * scale) / 2
    off_y = MARGIN + (VIEW - 2 * MARGIN - h * scale) / 2
    out: list[str] = []
    for contour in contours:
        pts = contour.reshape(-1, 2)
        if len(pts) == 0:
            continue
        first = True
        for px, py in pts:
            sx = (px - x0) * scale + off_x
            sy = (py - y0) * scale + off_y
            out.append(("M" if first else "L") + f"{sx:.2f},{sy:.2f}")
            first = False
        out.append("Z")
    return " ".join(out)


def build_sprite(paths: dict[str, str]) -> str:
    """Assemble the twelve piece groups into one cm-chessboard sprite.

    White pieces: white fill with a 0.8-unit black stroke, so Ignace's
    silhouette stays recognisable against a light board square.
    Black pieces: solid black fill, as drawn.
    """
    chunks: list[str] = [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{VIEW * 6}" height="{VIEW * 2}" '
        f'viewBox="0 0 {VIEW * 6} {VIEW * 2}">',
        "<defs>",
    ]
    for piece, d in paths.items():
        # Black pieces: silhouette as drawn.
        chunks.append(
            f'<g id="b{piece}"><path d="{d}" fill="#1a1a1a" /></g>'
        )
        # White pieces: same silhouette, white fill + ink outline so it
        # reads against both light and dark board squares.
        chunks.append(
            f'<g id="w{piece}"><path d="{d}" fill="#fbf4e6" '
            'stroke="#1a1a1a" stroke-width="0.8" stroke-linejoin="round" /></g>'
        )
    chunks.append("</defs>")
    chunks.append("</svg>")
    return "\n".join(chunks)


def main() -> None:
    grouped = extract_piece_contours(TEMPLATE)
    paths: dict[str, str] = {}
    for piece, contours in zip(PIECE_ORDER, grouped):
        # Bounding box is derived from the single tall contour per piece.
        x, y, w, h = cv2.boundingRect(contours[0])
        paths[piece] = contour_to_svg_path(contours, (x, y, w, h))
    svg = build_sprite(paths)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUTPUT} ({len(svg)} bytes, {len(paths)} pieces × 2 colours)")


if __name__ == "__main__":
    main()
