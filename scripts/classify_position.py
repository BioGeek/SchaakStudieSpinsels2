"""Derive a starting FEN from a study's diagram image.

Supersedes scripts/pdf_processing.py's OpenCV template-matching
classifier, which mis-classified kings as knights because it compared
against single-colour templates.

Two-pass approach:
  1. Shape matching via Hu moments — colour- and scale-invariant, so a
     white king and a black king that use the same silhouette produce
     the same feature vector. Classifies piece type.
  2. Mean-brightness inside the piece's foreground mask classifies
     colour: dark mean → black, light mean → white.

Ground-truth validation is straightforward: the book ships an index of
"<GBR> <wk_sq><bk_sq>" lines. After classification we check that the
kings it found sit on the index's squares; a mismatch prints a warning
and leaves the FEN marked low-confidence.

Usage:
    uv run python scripts/classify_position.py \
        --diagram data/exemplar/1/diagram_region.png \
        --gbr "4001.00 d1b3"

Emits JSON to stdout: {"fen": "...", "kings_ok": true, "warnings": []}.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "data" / "template.png"

# The six silhouettes in data/template.png appear in this left-to-right order
# (the labels beneath them read: Koning, Dame, Toren, Loper, Paard, Pion).
# cm-chessboard / FEN uses the English letters, uppercase for white pieces.
PIECE_ORDER = ["K", "Q", "R", "B", "N", "P"]


# Size to which detected silhouettes and templates are resized for
# direct-pixel correlation. 64 px preserves the top-of-piece details
# that distinguish queen (spiky crown), rook (flat battlements), king
# (cross), and bishop (mitre).
REF_SIZE = 64
# Fraction of the silhouette (from the top) to weight more heavily in
# shape matching. The body of every piece is a similar tapered column;
# the distinguishing features all sit up top.
HEAD_FRAC = 0.4
HEAD_WEIGHT = 3.0


@dataclass
class Template:
    letter: str             # "K", "Q", "R", "B", "N", "P"
    mask: np.ndarray        # REF_SIZE × REF_SIZE binary silhouette (0 / 255)
    aspect: float           # h/w of the silhouette's bounding box


def _normalize_silhouette(binary: np.ndarray) -> np.ndarray:
    """Crop to the silhouette's bounding box and resize to REF_SIZE × REF_SIZE.

    Uses uniform (non-aspect-preserving) resize because aspect-preserving
    variants made match quality worse empirically on the exemplar set —
    the distortion is symmetric so both detected piece and template stretch
    identically, preserving their relative shape similarity.
    """
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return np.zeros((REF_SIZE, REF_SIZE), dtype=np.uint8)
    c = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)
    crop = binary[y : y + h, x : x + w]
    return cv2.resize(crop, (REF_SIZE, REF_SIZE), interpolation=cv2.INTER_AREA)


def load_piece_templates(path: Path) -> list[Template]:
    """Extract each piece's normalized binary silhouette from data/template.png.

    Each template is rendered at REF_SIZE × REF_SIZE so downstream
    classification can do a straight pixel-wise correlation against a
    same-size silhouette extracted from a board square.
    """
    bgr = cv2.imread(str(path))
    if bgr is None:
        raise FileNotFoundError(path)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    heights = [cv2.boundingRect(c)[3] for c in contours]
    max_h = max(heights)
    glyphs = sorted(
        [c for c in contours if cv2.boundingRect(c)[3] >= max_h * 0.4],
        key=lambda c: cv2.boundingRect(c)[0],
    )[: len(PIECE_ORDER)]

    templates: list[Template] = []
    for letter, c in zip(PIECE_ORDER, glyphs):
        x, y, w, h = cv2.boundingRect(c)
        crop = thresh[y : y + h, x : x + w]
        mask = cv2.resize(crop, (REF_SIZE, REF_SIZE), interpolation=cv2.INTER_AREA)
        templates.append(Template(letter=letter, mask=mask, aspect=h / w))
    return templates


def find_board_bbox(img_gray: np.ndarray) -> tuple[int, int, int, int]:
    """Locate the 8×8 board inside a diagram-region image.

    The book draws a solid rectangular border around every diagram. We
    find the largest approximately-square contour whose bounding box is
    plausibly the board — at least 200px per side, aspect ratio ~1.
    """
    _, thresh = cv2.threshold(img_gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    best: tuple[int, int, int, int] | None = None
    best_area = 0
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w < 100 or h < 100:
            continue
        ratio = w / h
        if not (0.9 < ratio < 1.1):
            continue
        area = w * h
        if area > best_area:
            best = (x, y, w, h)
            best_area = area
    if best is None:
        raise RuntimeError("could not locate 8×8 board in diagram image")
    return best


def split_into_squares(board: np.ndarray) -> list[np.ndarray]:
    """Return 64 sub-images in a1, b1, …, h1, a2, … order (FEN rank order)."""
    h, w = board.shape[:2]
    sh, sw = h / 8, w / 8
    squares: list[np.ndarray] = []
    # FEN rank 8 is at the top of the image; rank 1 is at the bottom.
    for row in range(8):  # row 0 = rank 8
        for col in range(8):  # col 0 = file a
            y0, y1 = int(row * sh), int((row + 1) * sh)
            x0, x1 = int(col * sw), int((col + 1) * sw)
            squares.append(board[y0:y1, x0:x1])
    return squares


def classify_square(
    sq_bgr: np.ndarray, templates: list[Template]
) -> tuple[str, str] | None:
    """Return (colour, piece_letter) or None if the square is empty.

    Two-pass approach because white pieces are drawn as light bodies
    with thin dark outlines: a simple "deviates from median" mask picks
    up mostly the outline, which (a) looks "black" on average and (b)
    has a different shape than the solid silhouette templates.

      1. Loose mask (abs-deviation > 40) flags *any* ink / highlight on
         the square. Used only to gate "empty or not" and to decide
         colour via the 90th-percentile brightness — for white pieces
         the body pixels dominate that quantile even though the mean is
         pulled down by the outline.
      2. Colour-aware solid mask: once colour is known, threshold the
         original grey for *dark* pixels (black pieces) or *light*
         pixels (white pieces). That yields the filled silhouette that
         matches cleanly against the template Hu moments.
    """
    gray = cv2.cvtColor(sq_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    # Trim a ~10% border to avoid the checker-boundary artefacts.
    pad_y, pad_x = int(h * 0.1), int(w * 0.1)
    inner = gray[pad_y : h - pad_y, pad_x : w - pad_x]

    # Estimate the square's background tone from its four corners —
    # piece silhouettes never reach the corners of a square, so the
    # corners sample the clean board colour even when the piece occupies
    # the entire centre. The plain median of `inner` flips sign when
    # the piece is larger than half the square (e.g. a queen on her own
    # file), which made occupancy detection invert.
    ih, iw = inner.shape
    cs = max(3, min(ih, iw) // 6)
    corners = np.concatenate([
        inner[:cs, :cs].ravel(),
        inner[:cs, iw - cs:].ravel(),
        inner[ih - cs:, :cs].ravel(),
        inner[ih - cs:, iw - cs:].ravel(),
    ])
    bg = float(np.median(corners))
    diff = np.abs(inner.astype(np.int16) - bg).astype(np.uint8)
    _, any_mask = cv2.threshold(diff, 40, 255, cv2.THRESH_BINARY)
    # White pieces render with fuzzy anti-aliased edges; morphological
    # closing fills tiny gaps inside the silhouette and opening clears
    # isolated speckle. That makes the resulting contour match the
    # solid-template silhouette more faithfully.
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    any_mask = cv2.morphologyEx(any_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    any_mask = cv2.morphologyEx(any_mask, cv2.MORPH_OPEN, kernel, iterations=1)

    occupied_ratio = float(any_mask.mean()) / 255.0
    if occupied_ratio < 0.05:
        return None

    piece_pixels = inner[any_mask > 0]
    if piece_pixels.size == 0:
        return None

    # Shape: `any_mask` (pixels that deviate from the square's
    # background tone) already captures the silhouette for both black
    # pieces (~40 on ~170 dark squares or ~255 light squares) and
    # white pieces (the book renders them as mid-grey ~190, which
    # deviates clearly from both light and dark squares). Use the
    # largest contour of that mask.
    contours, _ = cv2.findContours(any_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    contour = max(contours, key=cv2.contourArea)
    if cv2.contourArea(contour) < 30:
        return None
    x, y, bw, bh = cv2.boundingRect(contour)

    # Colour: mean brightness of the silhouette's interior. White
    # pieces are drawn as mid-grey (~190), black pieces as near-black
    # (~40). The threshold sits comfortably between.
    piece_mean = float(piece_pixels.mean())
    colour = "w" if piece_mean > 100 else "b"

    aspect = bh / max(bw, 1)

    # Resize the detected silhouette to the same REF_SIZE used for
    # templates, then measure similarity as the fraction of overlapping
    # pixels (intersection-over-union of the binary masks). Works
    # well on low-resolution glyphs where Hu moments compress away
    # the small distinguishing features (queen points, king cross,
    # knight's horse head).
    piece_mask = _normalize_silhouette(any_mask)
    head_rows = int(REF_SIZE * HEAD_FRAC)
    piece_head = piece_mask[:head_rows]

    def iou(a: np.ndarray, b: np.ndarray) -> float:
        inter = float(np.logical_and(a > 0, b > 0).sum())
        union = float(np.logical_or(a > 0, b > 0).sum())
        return inter / union if union > 0 else 0.0

    def distance(t: Template) -> float:
        # Combined IoU: the whole silhouette plus a head-region boost.
        # The body of every piece is a tapered column, so the top-of-
        # piece region (crown vs battlements vs cross vs mitre) carries
        # the signal that separates queen from rook.
        whole = iou(piece_mask, t.mask)
        head = iou(piece_head, t.mask[:head_rows])
        combined = (whole + HEAD_WEIGHT * head) / (1.0 + HEAD_WEIGHT)
        return (1.0 - combined) + 0.5 * abs(aspect - t.aspect)

    best = min(templates, key=distance)
    return colour, best.letter


def ranks_to_fen(ranks: list[list[str]]) -> str:
    """Convert a rank-major 2D list of cells (piece letters or '.') into FEN."""
    out: list[str] = []
    for rank in ranks:
        s = ""
        empty = 0
        for cell in rank:
            if cell == ".":
                empty += 1
            else:
                if empty:
                    s += str(empty)
                    empty = 0
                s += cell
        if empty:
            s += str(empty)
        out.append(s)
    return "/".join(out) + " w - - 0 1"


def square_name(col: int, row: int) -> str:
    """(col=0,row=0) is a8 (top-left in our image); (col=7,row=7) is h1."""
    file = "abcdefgh"[col]
    rank = 8 - row
    return f"{file}{rank}"


def _sq_to_rc(sq: str) -> tuple[int, int]:
    """Convert "d1" → (row=7, col=3) in our rank-major 2D grid."""
    col = ord(sq[0]) - ord("a")
    row = 8 - int(sq[1])
    return row, col


def apply_gbr_king_correction(
    ranks: list[list[str]], gbr: str
) -> tuple[list[list[str]], bool]:
    """Overwrite the two king squares using the GBR string.

    The book's GBR line ends with two file/rank tokens (e.g.
    "4001.00 d1b3" — white king d1, black king b3). Wherever the
    classifier placed kings, wipe them; then set K/k on the GBR's
    squares. Returns (new_ranks, did_correct).
    """
    m = re.search(r"([a-h][1-8])([a-h][1-8])", gbr)
    if not m:
        return ranks, False
    wk_sq, bk_sq = m.group(1), m.group(2)

    # Remove any K/k the classifier produced elsewhere.
    fixed = [row[:] for row in ranks]
    for r in range(8):
        for c in range(8):
            if fixed[r][c] in ("K", "k"):
                fixed[r][c] = "."

    wr, wc = _sq_to_rc(wk_sq)
    br, bc = _sq_to_rc(bk_sq)
    fixed[wr][wc] = "K"
    fixed[br][bc] = "k"
    return fixed, True


def classify(diagram_path: Path, gbr: str | None = None) -> dict:
    img = cv2.imread(str(diagram_path))
    if img is None:
        raise FileNotFoundError(diagram_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    x, y, w, h = find_board_bbox(gray)
    board = img[y : y + h, x : x + w]
    # Trim the thin 2–3 px border drawn around the board.
    trim = max(2, min(w, h) // 40)
    board = board[trim:-trim, trim:-trim]

    templates = load_piece_templates(TEMPLATE)
    squares = split_into_squares(board)

    ranks: list[list[str]] = []
    located: list[tuple[str, str, str]] = []  # (letter, colour, square_name)
    for row in range(8):
        rank_cells: list[str] = []
        for col in range(8):
            sq = squares[row * 8 + col]
            found = classify_square(sq, templates)
            if found is None:
                rank_cells.append(".")
            else:
                colour, letter = found
                cell = letter.upper() if colour == "w" else letter.lower()
                rank_cells.append(cell)
                located.append((letter, colour, square_name(col, row)))
        ranks.append(rank_cells)

    warnings: list[str] = []
    kings_ok = True
    if gbr:
        m = re.search(r"([a-h][1-8])([a-h][1-8])", gbr)
        if m:
            wk, bk = m.group(1), m.group(2)
            found_kings = {(c, s): True for letter, c, s in located if letter == "K"}
            if not found_kings.get(("w", wk)):
                warnings.append(
                    f"white king: classifier guessed "
                    f"{[s for letter, c, s in located if letter == 'K' and c == 'w']}, "
                    f"GBR says {wk} — applying correction"
                )
                kings_ok = False
            if not found_kings.get(("b", bk)):
                warnings.append(
                    f"black king: classifier guessed "
                    f"{[s for letter, c, s in located if letter == 'K' and c == 'b']}, "
                    f"GBR says {bk} — applying correction"
                )
                kings_ok = False
            # Snap kings onto their GBR squares whenever GBR is provided.
            ranks, _ = apply_gbr_king_correction(ranks, gbr)

    fen = ranks_to_fen(ranks)

    return {
        "fen": fen,
        "kings_ok": kings_ok,
        "warnings": warnings,
        "pieces": [
            {"letter": letter, "colour": c, "square": s} for letter, c, s in located
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--diagram", type=Path, required=True)
    ap.add_argument("--gbr", type=str, default=None,
                    help="GBR string (e.g. '4001.00 d1b3') for the kings-square cross-check")
    args = ap.parse_args()

    result = classify(args.diagram, args.gbr)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
