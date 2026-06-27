#!/usr/bin/env python3
"""Render a study's variant tree as an SVG — a bird's-eye view of every line a
reader must hold in their head. Reads src/content/studies/NNN.json and lays the
move tree out as an indented outline: the trunk, the top-level variants (A, B…),
and their sub-variant tries. Transpositions are detected from the data (a
side-line whose final position re-appears in the main line is labelled
"→ zet N"), so the back-references are accurate, not hand-typed.

Usage: uv run python scripts/variant_tree_svg.py --study 1 [--out path.svg]
"""
import argparse
import html
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUDY_DIR = ROOT / "src" / "content" / "studies"

# palette (matches the site)
PAPER = "#fbf4e6"
INK = "#2b2118"
INK_SOFT = "#6a5f4b"
GOLD = "#b8923f"
ACCENT = "#7a1f0e"
LINE = "#cdbb91"

ROW_H = 30
INDENT = 26
PAD_X = 22
PAD_TOP = 70
CHAR_W = 7.85   # monospace 13px (ui-monospace advance width)
MOVE_FONT = 13


def move_number(ply):
    return (ply + 1) // 2


def is_white(ply):
    return ply % 2 == 1


def line_text(moves):
    """Format a ply list as chess notation: '2…Dd8+ 3.Kc2 Dg8 4.De2 …'."""
    out = []
    for i, m in enumerate(moves):
        n, w = move_number(m["ply"]), is_white(m["ply"])
        if w:
            out.append(f"{n}.{m['nl']}")
        elif i == 0:
            out.append(f"{n}…{m['nl']}")
        else:
            out.append(m["nl"])
    return " ".join(out)


def norm(fen):
    return " ".join(fen.split()[:2])  # placement + side to move


def build(study):
    moves = study["moves"]
    by_id = {m["id"]: m for m in moves}
    by_var = defaultdict(list)
    for m in moves:
        by_var[m["variant"]].append(m)
    for v in by_var:
        by_var[v].sort(key=lambda m: m["ply"])

    # parent variant + branch ply (the move in the parent we hang off)
    parent_var = {}
    branch_ply = {}
    for v, ms in by_var.items():
        p = ms[0]["parent"]
        if p is None:
            parent_var[v] = None
            branch_ply[v] = 0
        else:
            pm = by_id[p]
            parent_var[v] = pm["variant"]
            branch_ply[v] = pm["ply"]

    depth = {}
    def d(v):
        if v not in depth:
            depth[v] = 0 if parent_var[v] is None else d(parent_var[v]) + 1
        return depth[v]
    for v in by_var:
        d(v)

    # DFS order: children sorted by branch ply then id
    children = defaultdict(list)
    for v in by_var:
        if parent_var[v] is not None:
            children[parent_var[v]].append(v)
    for p in children:
        children[p].sort(key=lambda v: (branch_ply[v], v))

    order = []
    def walk(v):
        order.append(v)
        for c in children[v]:
            walk(c)
    root = next(v for v in by_var if parent_var[v] is None)
    walk(root)

    # transposition target for a side-line: its last position seen in main/parent
    main_positions = {}  # norm(fen) -> move number, for the trunk
    for m in by_var[root]:
        main_positions.setdefault(norm(m["fenAfter"]), move_number(m["ply"]))

    rows = []
    for v in order:
        ms = by_var[v]
        dep = depth[v]
        kind = "trunk" if parent_var[v] is None else ("variant" if "." not in v else "side")
        label = ""
        if kind == "variant":
            label = f"Variant {v}"
        elif kind == "side":
            label = v.split(".")[-1] + ")"
        # transposition?: side-line last pos appears in parent or main
        note = ""
        if kind == "side":
            pv = parent_var[v]
            pos = dict(main_positions)
            for m in by_var.get(pv, []):
                pos.setdefault(norm(m["fenAfter"]), move_number(m["ply"]))
            tgt = pos.get(norm(ms[-1]["fenAfter"]))
            note = f"→ zet {tgt}" if tgt else ""
        elif kind == "variant":
            note = "remise" if study.get("stipulation") == "=" else "wit wint"
        rows.append({
            "depth": dep, "kind": kind, "label": label,
            "text": line_text(ms), "note": note, "var": v,
            "branch_ply": branch_ply[v], "parent": parent_var[v],
        })
    return rows, order, parent_var, depth


def render(study):
    rows, order, parent_var, depth = build(study)
    idx = {r["var"]: i for i, r in enumerate(rows)}

    # geometry
    def row_y(i):
        return PAD_TOP + i * ROW_H + ROW_H // 2
    def node_x(dep):
        return PAD_X + dep * INDENT

    # width: widest (label + text + note)
    maxw = 0
    for r in rows:
        lab = (len(r["label"]) + 2) if r["label"] else 0
        w = node_x(r["depth"]) + 16 + (lab + len(r["text"])) * CHAR_W + len(r["note"]) * 6.5 + 90
        maxw = max(maxw, w)
    W = int(maxw)
    H = PAD_TOP + len(rows) * ROW_H + 24

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
               f'font-family="ui-sans-serif,system-ui,sans-serif" role="img" '
               f'aria-label="Variantenboom studie {study["number"]}">')
    out.append(f'<rect width="{W}" height="{H}" rx="10" fill="{PAPER}"/>')
    # header
    num = study["number"]
    trunk = next(r for r in rows if r["kind"] == "trunk")
    res = "remise" if study.get("stipulation") == "=" else "wit wint"
    out.append(f'<text x="{PAD_X}" y="30" font-size="16" font-weight="700" '
               f'fill="{INK}">Variantenboom — studie {num}</text>')
    out.append(f'<text x="{PAD_X}" y="50" font-size="12.5" fill="{INK_SOFT}">'
               f'{html.escape(res)} · {html.escape(trunk["text"])}</text>')
    out.append(f'<line x1="{PAD_X}" y1="60" x2="{W-PAD_X}" y2="60" '
               f'stroke="{LINE}" stroke-width="1"/>')

    # connectors: per parent, a vertical spine + horizontal stub to each child
    kids = defaultdict(list)
    for r in rows:
        if r["parent"] is not None:
            kids[r["parent"]].append(r["var"])
    for pv, cs in kids.items():
        px = node_x(depth[pv]) + 9
        py = row_y(idx[pv])
        last_y = row_y(idx[cs[-1]])
        out.append(f'<path d="M {px} {py+9} V {last_y}" fill="none" '
                   f'stroke="{LINE}" stroke-width="1.5"/>')
        for c in cs:
            cy = row_y(idx[c]); cx = node_x(depth[c])
            out.append(f'<path d="M {px} {cy} H {cx-2}" fill="none" '
                       f'stroke="{LINE}" stroke-width="1.5"/>')

    # rows
    for i, r in enumerate(rows):
        y = row_y(i); x = node_x(r["depth"])
        if r["kind"] == "trunk":
            out.append(f'<circle cx="{x+9}" cy="{y}" r="6" fill="{GOLD}"/>')
        elif r["kind"] == "variant":
            out.append(f'<rect x="{x+3}" y="{y-6}" width="12" height="12" rx="2" '
                       f'fill="{ACCENT}"/>')
        else:
            out.append(f'<circle cx="{x+9}" cy="{y}" r="4" fill="none" '
                       f'stroke="{INK_SOFT}" stroke-width="1.5"/>')
        tx = x + 22
        if r["label"]:
            col = ACCENT if r["kind"] == "variant" else INK_SOFT
            wt = "700" if r["kind"] == "variant" else "600"
            out.append(f'<text x="{tx}" y="{y+4}" font-size="12.5" font-weight="{wt}" '
                       f'fill="{col}">{html.escape(r["label"])}</text>')
            tx += (len(r["label"]) + 2) * (7.0 if r["kind"] == "variant" else 6.5)
        col = INK if r["kind"] in ("trunk", "variant") else INK_SOFT
        wt = "700" if r["kind"] == "trunk" else "400"
        out.append(f'<text x="{tx}" y="{y+4}" font-size="{MOVE_FONT}" '
                   f'font-family="ui-monospace,Menlo,Consolas,monospace" '
                   f'font-weight="{wt}" fill="{col}">{html.escape(r["text"])}</text>')
        if r["note"]:
            nx = tx + len(r["text"]) * CHAR_W + 18
            ncol = GOLD if r["kind"] == "variant" else INK_SOFT
            out.append(f'<text x="{nx}" y="{y+4}" font-size="11.5" font-style="italic" '
                       f'fill="{ncol}">{html.escape(r["note"])}</text>')
    out.append("</svg>")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()
    study = json.loads((STUDY_DIR / f"{args.study:03d}.json").read_text())
    svg = render(study)
    out = Path(args.out) if args.out else (ROOT / "src" / "variant-trees" / f"{args.study:03d}.svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
