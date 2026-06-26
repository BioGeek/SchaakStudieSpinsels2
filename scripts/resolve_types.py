"""Resolve classifier piece-type transpositions using the solution as truth.

The diagram classifier finds piece *locations* and *colours* reliably but
confuses similar silhouettes (queen/rook/bishop, knight/rook). The GBR code
fixes material *counts* — yet it is blind to a *swap* of two pieces of
different types, because the counts still match (a board with rook+bishop
transposed still has one rook and one bishop). Those swaps are the dominant
remaining error and slip straight past the GBR material correction.

The real disambiguator is the solution: the book's moves are only legal from
the true position. This module enumerates every officer-type assignment that
keeps the GBR material counts (classifier colours and all king/pawn squares
fixed), parses the study against each, and keeps the assignment whose move tree
runs deepest. A wrong assignment makes the real first move illegal, so it parses
to a near-empty tree; the true position parses the whole solution.

Only invoked when the classifier FEN fails to parse the full set of move tokens,
so studies the classifier already gets right pay nothing.
"""
from __future__ import annotations

import contextlib
import io
import itertools

import chess

from parse_study import (
    _is_clean_move_row,
    extract_moves_from_lines,
    parse_study,
    scrub_controls,
    split_sections,
    tokenize_body,
)

_OFFICERS = (chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT)
_LETTER_PT = (("Q", chess.QUEEN), ("R", chess.ROOK),
              ("B", chess.BISHOP), ("N", chess.KNIGHT))

# Guard against a combinatorial blow-up on a pathological position; real
# studies have a handful of officers, so the product stays tiny.
_MAX_CANDIDATES = 4096


def _count_plies(moves: list) -> int:
    n = 0
    for m in moves:
        n += 1
        for v in m.get("variations") or []:
            n += _count_plies(v.get("moves", []))
    return n


def _expected_plies(text: str) -> int:
    """Upper bound on parseable plies: every move token the book prints."""
    toks = tokenize_body(split_sections(scrub_controls(text))["body"])
    clean = [
        ln
        for t in toks
        if t["kind"] == "moves"
        for ln in t["lines"]
        if _is_clean_move_row(ln)
    ]
    return len(extract_moves_from_lines(clean))


def _score(fen: str, text: str, region: dict) -> int:
    try:
        # Each candidate parse logs illegal-move warnings; mute them so the
        # search doesn't drown the build output.
        with contextlib.redirect_stderr(io.StringIO()):
            result = parse_study(
                text, fen, region["chapter_num"], region["chapter_name"],
                region["number"],
            )
    except Exception:
        return -1
    return _count_plies(result.get("moves", []))


def _required_officers(gbr_material: dict) -> dict[bool, list[int]]:
    req: dict[bool, list[int]] = {chess.WHITE: [], chess.BLACK: []}
    for letter, pt in _LETTER_PT:
        w, b = gbr_material[letter]
        req[chess.WHITE] += [pt] * w
        req[chess.BLACK] += [pt] * b
    return req


def resolve_types(
    classifier_fen: str, text: str, region: dict, gbr_material: dict | None
) -> dict:
    """Try to repair a classifier officer-type swap against the solution.

    Returns a dict: {fen, changed, base_plies, best_plies, reason}. The returned
    FEN is the classifier's own unless a strictly deeper-parsing, GBR-consistent
    type assignment exists.
    """
    out = {
        "fen": classifier_fen,
        "changed": False,
        "base_plies": -1,
        "best_plies": -1,
        "reason": "",
    }
    if not gbr_material:
        out["reason"] = "no GBR material"
        return out
    try:
        board = chess.Board(classifier_fen)
    except ValueError:
        out["reason"] = "unparseable classifier FEN"
        return out

    base = _score(classifier_fen, text, region)
    out["base_plies"] = out["best_plies"] = base

    # The classifier already parses the whole solution → nothing to fix.
    if base >= _expected_plies(text):
        out["reason"] = "classifier FEN parses fully"
        return out

    officer_sqs: dict[bool, list[int]] = {chess.WHITE: [], chess.BLACK: []}
    for sq, piece in board.piece_map().items():
        if piece.piece_type in _OFFICERS:
            officer_sqs[piece.color].append(sq)

    req = _required_officers(gbr_material)
    # A pure swap leaves counts intact; a count mismatch is a different failure
    # (missing/extra piece) that needs a manual diagram override, not this.
    for colour in (chess.WHITE, chess.BLACK):
        if len(officer_sqs[colour]) != len(req[colour]):
            out["reason"] = "officer count != GBR (not a pure swap)"
            return out

    per_colour = {}
    total = 1
    for colour in (chess.WHITE, chess.BLACK):
        perms = {tuple(p) for p in itertools.permutations(req[colour])}
        per_colour[colour] = [dict(zip(officer_sqs[colour], p)) for p in perms]
        total *= len(per_colour[colour])
    if total > _MAX_CANDIDATES:
        out["reason"] = f"too many candidates ({total})"
        return out

    best_fen, best_score = classifier_fen, base
    for wa in per_colour[chess.WHITE]:
        for ba in per_colour[chess.BLACK]:
            cand = board.copy()
            for sq, pt in {**wa, **ba}.items():
                existing = cand.piece_at(sq)
                assert existing is not None  # sq came from the officer scan
                cand.set_piece_at(sq, chess.Piece(pt, existing.color))
            fen = cand.fen()
            if fen == classifier_fen:
                continue
            s = _score(fen, text, region)
            if s > best_score:
                best_fen, best_score = fen, s

    if best_fen != classifier_fen:
        out.update(
            fen=best_fen,
            changed=True,
            best_plies=best_score,
            reason=f"type swap resolved via solution ({base} -> {best_score} plies)",
        )
    else:
        out["reason"] = f"no deeper assignment found (base {base} plies)"
    return out
