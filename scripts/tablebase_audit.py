#!/usr/bin/env python3
"""Audit each study's STARTING position against its stipulation using the Lichess
tablebase (https://tablebase.lichess.ovh — 7-piece complete + partial 8-piece).

`verify_studies.py` only checks legality + GBR material + move-tree consistency;
it CANNOT tell whether the solution actually achieves its goal. A study whose
start position is theoretically a draw but is labelled "+win" (a wrong FEN, wrong
side-to-move, or mis-read +/= glyph) still passes verify. The tablebase is an
independent oracle: a "+" study must be a tablebase win for the stronger side, a
"=" study must be a draw.

Studies whose verdict matches the stipulation are stamped `"tablebaseVerified":
true` (with --write) so the check isn't re-run and the UI can show a badge.
Re-running skips already-verified studies (unless --recheck); positions with >8
pieces, or 8-piece positions not yet in the partial tablebase, report SKIP and
stay unverified — re-run later as tablebase coverage grows.

Usage:
  uv run python scripts/tablebase_audit.py            # report only
  uv run python scripts/tablebase_audit.py --write    # stamp tablebaseVerified on OK studies
  uv run python scripts/tablebase_audit.py --recheck  # re-query even already-verified studies
"""
import argparse
import glob
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import chess

ROOT = Path(__file__).resolve().parent.parent
STUDY_DIR = ROOT / "src" / "content" / "studies"

WIN = {"win", "cursed-win", "maybe-win"}
LOSS = {"loss", "blessed-loss", "maybe-loss"}
INCONCLUSIVE = {None, "unknown"}

_CACHE: dict[str, str | None] = {}


def tablebase_category(fen: str) -> str | None:
    """Lichess tablebase WDL category from the side-to-move's perspective."""
    if fen in _CACHE:
        return _CACHE[fen]
    url = "https://tablebase.lichess.ovh/standard?" + urllib.parse.urlencode({"fen": fen})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                _CACHE[fen] = json.load(resp).get("category")
                return _CACHE[fen]
        except Exception:
            if attempt == 2:
                return "ERR"
            time.sleep(1.0)


def verdict(fen: str, stipulation: str) -> tuple[str, str | None]:
    """Return (verdict, category). verdict in OK/MISMATCH/REVIEW/SKIP/ERR."""
    board = chess.Board(fen)
    if len(board.piece_map()) > 8:
        return "SKIP", "skip>8"
    cat = tablebase_category(fen)
    if isinstance(cat, str) and cat.startswith("ERR"):
        return "ERR", cat
    if cat in INCONCLUSIVE:
        return "SKIP", cat
    stm_white = board.turn == chess.WHITE
    white_wins = (stm_white and cat in WIN) or ((not stm_white) and cat in LOSS)
    white_loses = (stm_white and cat in LOSS) or ((not stm_white) and cat in WIN)
    if stipulation == "+":
        return ("OK" if white_wins else "MISMATCH"), cat
    if stipulation == "=":
        if cat == "draw":
            return "OK", cat
        return ("REVIEW" if not (white_wins or white_loses) else "MISMATCH"), cat
    return "?", cat


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="stamp tablebaseVerified:true on studies that match")
    ap.add_argument("--recheck", action="store_true",
                    help="re-query studies already marked tablebaseVerified")
    args = ap.parse_args()

    counts: dict[str, int] = {}
    flagged: list[tuple] = []
    newly_marked = 0
    for path in sorted(glob.glob(str(STUDY_DIR / "*.json"))):
        d = json.loads(Path(path).read_text())
        n, stip = d["number"], d.get("stipulation", "+")
        if d.get("tablebaseVerified") and not args.recheck:
            counts["already-verified"] = counts.get("already-verified", 0) + 1
            continue
        v, cat = verdict(d["fen"], stip)
        time.sleep(0.2)
        counts[v] = counts.get(v, 0) + 1
        if v in ("MISMATCH", "REVIEW"):
            flagged.append((n, stip, cat, v, d.get("curated", False)))
        elif v == "OK" and args.write and not d.get("tablebaseVerified"):
            d["tablebaseVerified"] = True
            Path(path).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
            newly_marked += 1

    print("verdicts:", counts)
    if args.write:
        print(f"newly stamped tablebaseVerified: {newly_marked}")
    if flagged:
        print("\n=== FLAGGED (tablebase contradicts stipulation — likely wrong FEN/stipulation) ===")
        print(f'{"study":>5} {"stip":>4} {"tb-category":>12} {"verdict":>8} curated')
        for n, stip, cat, v, cur in sorted(flagged):
            print(f"{n:>5} {stip:>4} {str(cat):>12} {v:>8} {cur}")
    else:
        print("\nNo mismatches among the studies checked.")


if __name__ == "__main__":
    main()
