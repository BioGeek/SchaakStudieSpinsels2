"""Parse an extracted study's plain text into a structured JSON.

Input: the `text.txt` that `scripts/study_extractor.py` emits per study,
plus a starting FEN (derived from the diagram — hand-provided for the
exemplar set, automated later).

Output: JSON matching src/content/config.ts's `studies` schema:
  { number, chapter, chapterNumber, source, gbr, fen, stipulation,
    moves: [{id, ply, san, nl, fenAfter, variant, parent}],
    prose: { nl: { before, after } } }

Scope for this first cut:
  * Extract header, source, stipulation, GBR code.
  * Parse the main line (sequence of white/black move pairs).
  * Parse top-level variants (Variant A / B) as distinct branches.
  * Parse nested sub-variants (a), b), ...) as branches off the parent.
  * Validate each move by feeding Dutch→English SAN to python-chess
    and capturing the FEN after each ply.
  * Prose (paragraphs between move blocks) is captured into
    `prose.nl.before` / `prose.nl.after`.
  * Back-references (`zie zet N.`) are preserved verbatim in prose.

Out of scope for now (parsed as prose, not clickable): inline side-lines
embedded between mainline moves (e.g. "4.Pd2? Dc8+ ... (zie zei 4.)").
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

import chess

ROOT = Path(__file__).resolve().parent.parent

# Dutch → English piece-letter map for chess.js-style SAN.
NL_TO_EN = {"K": "K", "D": "Q", "T": "R", "L": "B", "P": "N"}

# Match a single move token in Dutch notation.
# Examples: Pa5+, Ka2, Pc4, Da4+?, Dd8+, Kb6/Dxb3, Pxc7, f8D, f8=D,
# Dxa4/Dxb3 (alternate-capture shorthand — we keep the first alternative).
#
# Piece prefix: one of K D T L P (optional for pawn moves).
# Disambiguator: optional file (a-h) or rank (1-8) between piece and dest.
# Capture: optional "x" or ":".
# Destination: a1..h8.
# Promotion: "=D|T|L|P" or (Dutch shorthand) trailing "D|T|L|P" on rank-1/8.
# Annotation tail: zero or more of "+", "#", "!", "?", "~".
MOVE_RE = re.compile(
    r"""
    ([KDTLP])?                 # piece
    ([a-h]?[1-8]?)             # disambiguator (file and/or rank)
    ([x:])?                    # capture
    ([a-h][1-8])               # destination
    (?:=([DTLP])|([DTLP])(?=$|[^a-h0-9]))?  # promotion (=X, or Dutch trailing X)
    ([+#!?~]*)                 # annotations
    """,
    re.VERBOSE,
)

# A move-number prefix like "1." or "1…" (ellipsis for black-only replies)
MOVE_NUM_RE = re.compile(r"(\d+)\.(?:\.\.\.|…)?")


@dataclass
class Move:
    id: str
    ply: int
    san: str
    nl: str
    fenAfter: str
    variant: str = "main"
    parent: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def scrub_controls(s: str) -> str:
    """Drop C0 control chars except tab/LF/CR (same defensive scrub as port_pelican_pages)."""
    return "".join(c for c in s if ord(c) >= 0x20 or c in "\t\n\r")


def dutch_to_san(move: str) -> str:
    """Translate a Dutch notation move to English SAN for python-chess.

    Handles piece-letter substitution at the start and on disambiguators
    ("Dxa4" -> "Qxa4"), promotion ("f8D" or "f8=D" -> "f8=Q"), and strips
    annotation marks ("?"/"!"/"~") that python-chess rejects. Returns the
    cleaned SAN; callers keep the original Dutch for display.
    """
    # Leading piece letter
    if move and move[0] in NL_TO_EN:
        move = NL_TO_EN[move[0]] + move[1:]
    # Promotion: =D → =Q, and Dutch-shorthand rank-1/8 trailer like "f8D" → "f8=Q"
    move = re.sub(r"=([DTLP])", lambda m: "=" + NL_TO_EN[m.group(1)], move)
    move = re.sub(
        r"([a-h][18])([DTLP])(\b|[+#!?~]|$)",
        lambda m: m.group(1) + "=" + NL_TO_EN[m.group(2)] + m.group(3),
        move,
    )
    # Drop annotation marks that python-chess does not accept ("?", "!", "~").
    # Keep "+" and "#" since they encode legal check / mate state.
    move = re.sub(r"[?!~]+", "", move)
    return move


def split_sections(text: str) -> dict:
    """Split the raw study text into head (header/source/GBR) + body chunks."""
    lines = text.splitlines()
    header_line = ""
    source = ""
    stipulation = ""
    gbr = ""

    body_start = 0
    # Header is the first non-empty line matching `- N -`
    header_re = re.compile(r"^\s*-\s*(\d+)\s*-\s*$")
    for i, line in enumerate(lines):
        if header_re.match(line):
            header_line = line.strip()
            body_start = i + 1
            break

    # Source: first non-empty, non-moves line after the header
    # Stipulation + GBR: a line containing "+" or "=" followed by the GBR code
    gbr_re = re.compile(r"\s*([+=])\s+(\d{4}\.\d{2})(?:\s+([a-h][1-8][a-h][1-8]))?")
    stip_idx = -1
    for i in range(body_start, min(body_start + 20, len(lines))):
        ln = lines[i].strip()
        if not ln:
            continue
        m = gbr_re.match(ln)
        if m:
            stipulation = m.group(1)
            gbr = m.group(2) + (f" {m.group(3)}" if m.group(3) else "")
            stip_idx = i
            break
        if not source:
            source = ln

    body_lines = lines[(stip_idx + 1 if stip_idx >= 0 else body_start):]
    return {
        "header": header_line,
        "source": source,
        "stipulation": stipulation,
        "gbr": gbr,
        "body": "\n".join(body_lines),
    }


# Match a move-list line. Accepts every move-number shape the book uses:
#   "1.Pa5+ Ka2"           — full move number then white's move
#   "2… Dd8+" / "2...Dd8+" — black-only reply (no period before ellipsis)
#   "a) 2.Da4+? Kb1 …"     — sub-variant prefix before a full move number
# Optional leading whitespace / "." / sub-variant label.
MOVE_LINE_RE = re.compile(r"^[\s.]*(?:[a-z]\))?\s*\d+\s*(?:\.+|…)")


def is_page_number(line: str) -> bool:
    """Strip stray printed page numbers like "   38" on their own line."""
    s = line.strip()
    return s.isdigit() and len(s) <= 4


def tokenize_body(body: str) -> list[dict]:
    """Group lines into move-blocks and prose-blocks, recognising variant headers.

    Returns a list of tokens:
      {"kind": "prose", "text": str}
      {"kind": "variant_header", "label": "A"|"B"|...}
      {"kind": "subvariant_header", "label": "a"|"b"|..., "tail": str}
      {"kind": "moves", "lines": [str]}
    """
    tokens: list[dict] = []
    current_moves: list[str] = []
    current_prose: list[str] = []

    variant_re = re.compile(r"^\s*Variant\s+([A-Z])\s*$")
    subvar_re = re.compile(r"^\s*([a-z])\)\s*(.*)$")

    def flush_prose():
        if current_prose:
            text = "\n".join(current_prose).strip()
            if text:
                tokens.append({"kind": "prose", "text": text})
            current_prose.clear()

    def flush_moves():
        if current_moves:
            tokens.append({"kind": "moves", "lines": list(current_moves)})
            current_moves.clear()

    for raw in body.splitlines():
        line = raw.rstrip()
        if is_page_number(line):
            continue
        m = variant_re.match(line)
        if m:
            flush_prose()
            flush_moves()
            tokens.append({"kind": "variant_header", "label": m.group(1)})
            continue
        m = subvar_re.match(line)
        if m:
            flush_prose()
            flush_moves()
            tokens.append({"kind": "subvariant_header", "label": m.group(1), "tail": m.group(2)})
            continue
        if MOVE_LINE_RE.match(line) or (line.lstrip().startswith("…") or line.lstrip().startswith("...")):
            flush_prose()
            current_moves.append(line)
            # A line containing a "(zie zet N.)" style back-reference marks
            # the end of an inline side-variant. Flush so the NEXT moves
            # block (main flow resumption) gets its own apply_moves call
            # with a fresh side-variant state.
            if "(zie z" in line.lower():
                flush_moves()
        elif not line.strip():
            # Blank line — end of a moves block or prose paragraph
            flush_moves()
            if current_prose and current_prose[-1] != "":
                current_prose.append("")
        else:
            flush_moves()
            current_prose.append(line)

    flush_prose()
    flush_moves()
    return tokens


def extract_moves_from_lines(lines: list[str]) -> list[tuple[int, bool, str]]:
    """Pull out Dutch move tokens with their move-number context from a block.

    Returns a list of (move_number, is_white, dutch_move) tuples. The
    move_number/is_white fields let downstream code compute proper plies
    for display (e.g. "3…" is move 3, black), without having to
    reconstruct the count from sequence.

    Handles:
      * ``1.Pa5+  Ka2`` — white then black under the same move number
      * ``2…  Dd8+`` (or ``2... Dd8+``) — black-only reply
      * ``a)  2.Da4+?`` — sub-variant prefix stripped
      * Parenthesised annotations and back-refs are dropped
      * Alternate-capture shorthand ``Dxa4/Dxb3`` keeps the first form
    """
    blob = " ".join(lines)
    # Drop parenthesised annotations / back-refs before tokenising.
    blob = re.sub(r"\([^)]*\)", " ", blob)
    # Drop sub-variant prefixes like "a)" or "b)" that sit at the head of a
    # line — they're structural, not part of any move token.
    blob = re.sub(r"\b[a-z]\)", " ", blob)

    out: list[tuple[int, bool, str]] = []
    current_num: int | None = None
    # True iff the next move token we consume is white's move for `current_num`.
    white_due = True

    def norm_token(tok: str) -> str | None:
        tok = tok.strip(".:,;")
        if not tok:
            return None
        if "/" in tok:
            tok = tok.split("/", 1)[0]  # keep first alternative
        if MOVE_RE.fullmatch(tok):
            return tok
        # Wildcard shorthand like "K~" (any king move, destination not
        # given). Destination gets resolved later in apply_moves.
        if re.fullmatch(r"[KDTLP]~[+#!?]*", tok):
            return tok
        return None

    # Scan the blob looking for move-number markers and move tokens in order.
    # Accept every form the book uses for the move-number prefix:
    #   "3."       — white's 3rd move follows
    #   "3…" / "3..." — black's 3rd move follows (no period before the ellipsis)
    #   "3.…" / "3. ..."  — same, with both a period and an ellipsis
    pattern = re.compile(
        r"(\d+)(\.(?:\.\.|…)?|…)"   # move number + marker (captures which kind)
        r"|(\.\.\.|…)"               # standalone ellipsis token
        r"|(\S+)"                    # any other non-whitespace token
    )
    for m in pattern.finditer(blob):
        num_match, marker, standalone_ell, tok_match = m.group(1), m.group(2), m.group(3), m.group(4)
        if num_match is not None:
            current_num = int(num_match)
            # Black-to-move iff the marker carries an ellipsis (the author
            # omitted white's move because it's the same as main).
            white_due = "…" not in marker and "..." not in marker
        elif standalone_ell is not None:
            white_due = False
        elif tok_match is not None:
            if current_num is None:
                continue
            tok = norm_token(tok_match)
            if tok is None:
                continue
            out.append((current_num, white_due, tok))
            # After consuming one move, toggle side for the next token under the
            # same move number. A following move-number marker will reset both.
            white_due = not white_due
    return out


def ply_for(move_number: int, is_white: bool) -> int:
    """Convert (move-number, side) to a 1-based absolute ply index."""
    return 2 * (move_number - 1) + (1 if is_white else 2)


def apply_moves(
    start_fen: str,
    tuples: list[tuple[int, bool, str]],
    variant: str,
    parent: str | None,
) -> tuple[list[Move], str | None]:
    """Feed a sequence of (move_num, is_white, dutch) moves into python-chess.

    The starting FEN must have the side-to-move that matches the first
    tuple's `is_white`. If python-chess rejects a move, we stop the
    variant at that ply rather than silently skipping it.
    """
    board = chess.Board(start_fen)
    out: list[Move] = []
    last_id: str | None = parent
    last_ply = 0
    in_inline = False
    for move_num, is_white, nl_move in tuples:
        ply = ply_for(move_num, is_white)
        # Inline side-variant detection. The book sometimes weaves a side
        # line into the main move list by repeating a move number, e.g.:
        #   4.De2
        #   4.Pd2? Dc8+ 5.Pc4 Dg8 6.De2+    <- inline side-line
        # 4...Dg3   <- main resumes (next MOVES block)
        # A tuple whose ply is ≤ the last successfully played ply means we
        # stepped backwards: enter inline-skip mode. Stay there for the
        # rest of this tuple list — the caller will feed us a fresh list
        # for the next block where the main variant resumes.
        if ply <= last_ply:
            in_inline = True
        if in_inline:
            continue
        san = dutch_to_san(nl_move)
        # The book uses "~" as a wildcard for "any move by this piece" (most
        # commonly "K~" for a forced king move whose square is immaterial).
        # python-chess doesn't understand that, so we pick any legal move
        # made by the matching piece type and use its SAN as a stand-in.
        if "~" in nl_move:
            piece_nl = nl_move.rstrip("+#!?~")[0] if nl_move else ""
            piece_en = NL_TO_EN.get(piece_nl)
            chosen = _pick_wildcard_move(board, piece_en)
            if chosen is None:
                print(
                    f"[warn] no legal {piece_nl}-move for wildcard '{nl_move}' "
                    f"at {move_num}.{'' if is_white else '…'} of variant '{variant}'",
                    file=sys.stderr,
                )
                break
            san = board.san(chosen)
            board.push(chosen)
            last_ply = ply
            move_id = f"{variant}.{ply}"
            out.append(Move(id=move_id, ply=ply, san=san, nl=nl_move,
                            fenAfter=board.fen(), variant=variant, parent=last_id))
            last_id = move_id
            continue
        try:
            move = board.parse_san(san)
        except (chess.IllegalMoveError, chess.InvalidMoveError, chess.AmbiguousMoveError, ValueError) as exc:
            print(
                f"[warn] failed to parse '{nl_move}' (-> '{san}') at "
                f"{move_num}.{'' if is_white else '…'} of variant '{variant}': {exc}",
                file=sys.stderr,
            )
            break
        board.push(move)
        last_ply = ply
        move_id = f"{variant}.{ply}"
        out.append(
            Move(
                id=move_id,
                ply=ply,
                san=san,
                nl=nl_move,
                fenAfter=board.fen(),
                variant=variant,
                parent=last_id,
            )
        )
        last_id = move_id
    return out, last_id


def parse_study(
    text: str,
    start_fen: str,
    chapter_num: int,
    chapter_name: str,
    study_number: int,
) -> dict:
    text = scrub_controls(text)
    sections = split_sections(text)
    tokens = tokenize_body(sections["body"])

    all_moves: list[Move] = []
    prose_before: list[str] = []
    prose_after: list[str] = []

    # State machine walking the tokens:
    #  - "main" variant is the trunk; its last move is the branch point for
    #    top-level variants A, B, ... (which continue black's reply to the
    #    main line's final white move).
    #  - Each variant tracks its own tail so a following "moves" block
    #    continues the same variant.
    current_variant = "main"
    main_end_id: str | None = None
    last_move_id_in_variant: dict[str, str | None] = {"main": None}
    any_move_seen = False

    for tok in tokens:
        kind = tok["kind"]
        if kind == "prose":
            (prose_after if any_move_seen else prose_before).append(tok["text"])
            continue

        if kind == "variant_header":
            current_variant = tok["label"]  # "A", "B", ...
            # Top-level variants branch from the end of the main line.
            last_move_id_in_variant[current_variant] = main_end_id
            continue

        if kind == "subvariant_header":
            # Sub-variant like "a) 2.Da4+? Kb1 …" BRANCHES BEFORE the move in
            # its enclosing variant that has the same move-number+side as its
            # first move. So "a) 2.Da4+?" (white's move 2) branches off the
            # ply just before the enclosing variant's white-move-2 — i.e. its
            # parent is the move at (first_sub_ply - 1) inside the enclosing
            # variant (or the start of the study if it would be ply 0).
            sub_label = f"{current_variant}.{tok['label']}"
            moves = extract_moves_from_lines([tok["tail"]])
            if not moves:
                last_move_id_in_variant[sub_label] = last_move_id_in_variant.get(current_variant)
                continue
            first_num, first_is_white, _ = moves[0]
            target_ply = ply_for(first_num, first_is_white) - 1
            parent = _find_parent_at_ply(all_moves, current_variant, target_ply)
            last_move_id_in_variant[sub_label] = parent
            start_fen_for_sub = _fen_at(all_moves, parent, start_fen)
            sub_moves, tail = apply_moves(start_fen_for_sub, moves, sub_label, parent)
            all_moves.extend(sub_moves)
            last_move_id_in_variant[sub_label] = tail
            any_move_seen = any_move_seen or bool(sub_moves)
            continue

        if kind == "moves":
            moves = extract_moves_from_lines(tok["lines"])
            if not moves:
                continue
            # A moves block that starts with move-number 1 after we've
            # already parsed moves is almost always a historical-game
            # quotation buried in the trailing prose — e.g. "Carel Mann
            # speelde in Caissa (1935): 1.Pa5+ Ka2 2.Pc4 …" at the end
            # of study #1, or the Kolpakov reference solution at the
            # tail of study #7. Treat as prose instead of continuing.
            if moves[0][0] == 1 and any_move_seen:
                prose_after.append(" ".join(tok["lines"]).strip())
                continue
            parent = last_move_id_in_variant.get(current_variant)
            # First block inside a non-main variant: the variant's first move
            # may not be at parent_ply + 1 (e.g. Variant A opens at "2…Dd8+"
            # which continues black's reply to main's 2.Pc4). Reuse the same
            # "branch before this ply" logic as sub-variants: position the
            # parent at (first_ply - 1) in the main line.
            if current_variant != "main" and parent == main_end_id:
                first_num, first_is_white, _ = moves[0]
                target_ply = ply_for(first_num, first_is_white) - 1
                parent = _find_parent_at_ply(all_moves, "main", target_ply) or main_end_id
            start_fen_for_variant = _fen_at(all_moves, parent, start_fen)
            new_moves, tail = apply_moves(
                start_fen_for_variant, moves, current_variant, parent
            )
            all_moves.extend(new_moves)
            last_move_id_in_variant[current_variant] = tail
            if current_variant == "main":
                main_end_id = tail
            any_move_seen = any_move_seen or bool(new_moves)

    result = {
        "number": study_number,
        "chapter": chapter_name,
        "chapterNumber": chapter_num,
        "source": sections["source"],
        "gbr": sections["gbr"],
        "fen": start_fen,
        "stipulation": sections["stipulation"],
        "moves": [m.to_dict() for m in all_moves],
        "prose": {
            "nl": {
                "before": "\n\n".join(p for p in prose_before if p),
                "after": "\n\n".join(p for p in prose_after if p),
            }
        },
    }
    return result


def _fen_at(moves: list[Move], move_id: str | None, start_fen: str) -> str:
    """Return the FEN after `move_id`, or the start FEN if id is None."""
    if move_id is None:
        return start_fen
    for m in moves:
        if m.id == move_id:
            return m.fenAfter
    return start_fen


_PIECE_MAP = {
    "K": chess.KING, "Q": chess.QUEEN, "R": chess.ROOK,
    "B": chess.BISHOP, "N": chess.KNIGHT, "P": chess.PAWN,
}


def _pick_wildcard_move(board: "chess.Board", piece_en: str | None) -> "chess.Move | None":
    """Pick a legal move made by pieces of the given English letter.

    Used for wildcard tokens like ``K~`` in the source text. Preferring
    king moves is fine for the common case; other piece wildcards are
    rare but handled for completeness. Returns None if no candidate.
    """
    if piece_en is None:
        return None
    piece_type = _PIECE_MAP.get(piece_en)
    if piece_type is None:
        return None
    for move in board.legal_moves:
        piece = board.piece_at(move.from_square)
        if piece and piece.piece_type == piece_type:
            return move
    return None


def _find_parent_at_ply(moves: list[Move], variant: str, target_ply: int) -> str | None:
    """Locate the move in `variant` at ``target_ply`` — the branch point.

    ``target_ply <= 0`` means branch at the very start of the study.
    Returns None (= start of study) if the requested ply was not played
    in that variant yet; the caller's apply_moves will then start from
    the starting FEN, which matches the semantics "branch before ply 1".
    """
    if target_ply <= 0:
        return None
    for m in moves:
        if m.variant == variant and m.ply == target_ply:
            return m.id
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", type=Path, required=True, help="path to text.txt from study_extractor")
    ap.add_argument("--region", type=Path, required=True, help="path to region.json from study_extractor")
    ap.add_argument("--fen", type=str, required=True, help="starting FEN for this study")
    ap.add_argument("--out", type=Path, required=True, help="output study JSON")
    args = ap.parse_args()

    region = json.loads(args.region.read_text(encoding="utf-8"))
    text = args.text.read_text(encoding="utf-8")

    result = parse_study(
        text=text,
        start_fen=args.fen,
        chapter_num=region["chapter_num"],
        chapter_name=region["chapter_name"],
        study_number=region["number"],
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {len(result['moves'])} moves parsed")


if __name__ == "__main__":
    main()
