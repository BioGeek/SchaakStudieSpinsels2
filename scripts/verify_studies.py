"""Validate built study JSONs against the book's own ground truth.

Each study carries a GBR material code (e.g. "4001.00 d1b3"), which the
book uses to specify exactly what is on the board. We decode it and check
that the study's starting FEN has the same material — the strongest cheap
correctness signal we have, since it catches the classifier's queen/rook/
bishop silhouette confusions that move parsing can't.

A study passes when:
  * its FEN material matches the GBR code, and
  * the kings sit on the GBR-specified squares, and
  * the parser produced at least one move.

Usage:
    uv run python scripts/verify_studies.py            # report all studies
    uv run python scripts/verify_studies.py --fail-only # only the failures
    uv run python scripts/verify_studies.py --json      # machine-readable
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import chess

ROOT = Path(__file__).resolve().parent.parent
STUDY_DIR = ROOT / "src" / "content" / "studies"

_OFFICERS = [
    ("Q", chess.QUEEN),
    ("R", chess.ROOK),
    ("B", chess.BISHOP),
    ("N", chess.KNIGHT),
    ("P", chess.PAWN),
]


def gbr_material(gbr: str) -> dict[str, tuple[int, int]] | None:
    """Decode 'DDDD.PP ...' into per-colour (white, black) piece counts."""
    m = re.match(r"\s*(\d)(\d)(\d)(\d)\.(\d)(\d)", gbr)
    if not m:
        return None

    def split(d: str) -> tuple[int, int] | None:
        d = int(d)
        for b in range(3):
            for w in range(3):
                if w + 3 * b == d:
                    return (w, b)
        return None

    q, r, b, n = (split(m.group(i)) for i in (1, 2, 3, 4))
    if None in (q, r, b, n):
        return None
    return {"Q": q, "R": r, "B": b, "N": n, "P": (int(m.group(5)), int(m.group(6)))}


def fen_material(fen: str) -> dict[str, tuple[int, int]]:
    board = chess.Board(fen)
    return {
        letter: (
            len(board.pieces(pt, chess.WHITE)),
            len(board.pieces(pt, chess.BLACK)),
        )
        for letter, pt in _OFFICERS
    }


def gbr_king_squares(gbr: str) -> tuple[str, str] | None:
    m = re.search(r"([a-h][1-8])([a-h][1-8])", gbr)
    return (m.group(1), m.group(2)) if m else None


def check(study: dict) -> dict:
    """Return {study, ok, reasons[]} for one parsed study."""
    reasons: list[str] = []
    gbr = study.get("gbr", "")
    fen = study["fen"]

    if not study.get("moves"):
        reasons.append("0 moves parsed")

    mat = gbr_material(gbr)
    if mat is None:
        reasons.append(f"unparseable GBR {gbr!r}")
    else:
        act = fen_material(fen)
        for k in mat:
            if mat[k] != act[k]:
                reasons.append(
                    f"{k} material GBR{mat[k]} != FEN{act[k]}"
                )

    ks = gbr_king_squares(gbr)
    if ks:
        board = chess.Board(fen)
        wk = chess.square_name(board.king(chess.WHITE)) if board.king(chess.WHITE) is not None else None
        bk = chess.square_name(board.king(chess.BLACK)) if board.king(chess.BLACK) is not None else None
        if (wk, bk) != ks:
            reasons.append(f"kings {(wk, bk)} != GBR {ks}")

    bad = first_inconsistent_move(study)
    if bad:
        reasons.append(f"move {bad} not reachable from its parent (broken move-tree)")

    return {"study": study["number"], "ok": not reasons, "reasons": reasons}


def first_inconsistent_move(study: dict) -> str | None:
    """Return the id of the first move whose SAN doesn't yield its recorded
    fenAfter from its parent's position, or None if the whole tree is sound.

    Each move must be legal from its parent (the study FEN for root moves) and
    land on exactly the position it claims. This catches inline side-lines that
    were merged into a variant with a wrong parent link — the kind of breakage
    a plain move-count check sails straight past.
    """
    by_id = {m["id"]: m for m in study["moves"]}
    for m in study["moves"]:
        parent_fen = study["fen"] if not m["parent"] else by_id.get(m["parent"], {}).get("fenAfter")
        if parent_fen is None:
            return m["id"]
        board = chess.Board(parent_fen)
        try:
            board.push_san(m["san"])
        except (chess.IllegalMoveError, chess.InvalidMoveError, chess.AmbiguousMoveError, ValueError):
            return m["id"]
        # Compare placement + side-to-move; ignore clock/ep fields.
        if board.fen().split()[:2] != m["fenAfter"].split()[:2]:
            return m["id"]
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fail-only", action="store_true", help="print only failing studies")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = ap.parse_args()

    results = []
    for path in sorted(STUDY_DIR.glob("*.json")):
        results.append(check(json.loads(path.read_text())))

    if args.json:
        print(json.dumps(results, indent=2))
        return

    passed = [r for r in results if r["ok"]]
    failed = [r for r in results if not r["ok"]]
    for r in results:
        if args.fail_only and r["ok"]:
            continue
        mark = "✓" if r["ok"] else "✗"
        detail = "" if r["ok"] else "  " + "; ".join(r["reasons"])
        print(f"{mark} study {r['study']:3d}{detail}")
    print(f"\n{len(passed)}/{len(results)} studies pass GBR/move verification "
          f"({len(failed)} need attention)")


if __name__ == "__main__":
    main()
