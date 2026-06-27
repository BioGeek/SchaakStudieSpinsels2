"""End-to-end: extract + classify + parse a single study into content.

Chains scripts/study_extractor.py, scripts/classify_position.py, and
scripts/parse_study.py into one command.

Usage:
    # Normal case: classifier figures out the FEN on its own.
    uv run python scripts/build_study.py --study 152

    # Override the FEN manually when the classifier can't distinguish
    # queen from rook (the known long-tail failure mode).
    uv run python scripts/build_study.py --study 1 \\
        --fen "2q5/1N6/8/8/4Q3/1k6/8/3K4 w - - 0 1"

    # Bulk-run for fan-out; skips studies where the classifier's
    # output has already been manually overridden via
    # data/exemplar/<N>/fen_override.txt.
    uv run python scripts/build_study.py --all
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from resolve_types import resolve_types
from study_extractor import list_studies
from verify_studies import gbr_material as decode_gbr_material

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "data" / "schaakstudiespinsels2.pdf"
EXEMPLAR_DIR = ROOT / "data" / "exemplar"
STUDY_CONTENT_DIR = ROOT / "src" / "content" / "studies"


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a subprocess, forwarding stderr to our own stderr."""
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kwargs)


def build_one(study_number: int, fen_override: str | None, force: bool = False) -> dict:
    """Run the extractor + classifier + parser for a single study.

    Returns a small status dict with counts + whether overrides were
    used, so the --all driver can summarise at the end.

    A study whose committed JSON is marked ``"curated": true`` was manually
    corrected (FEN override sidecar) or hand-built (the parser truncates it),
    and cannot be reproduced from a clean checkout — the override sidecars live
    under the gitignored ``data/exemplar/``. Such a study is skipped (preserving
    the committed JSON) unless ``force`` is set, so a bulk ``--all`` rebuild can
    never silently clobber hand-curated work.
    """
    json_path = STUDY_CONTENT_DIR / f"{study_number:03d}.json"
    if not force and json_path.exists():
        try:
            existing = json.loads(json_path.read_text())
        except (json.JSONDecodeError, OSError):
            existing = {}
        if existing.get("curated"):
            print(
                f"[{study_number}] curated study — skipping (pass --force to "
                f"rebuild from the diagram/overrides and overwrite it)",
                file=sys.stderr,
            )
            return {
                "study": study_number,
                "source": "curated-skip",
                "moves": len(existing.get("moves", [])),
                "fen": existing.get("fen"),
                "skipped": True,
            }

    out = EXEMPLAR_DIR / str(study_number)
    out.mkdir(parents=True, exist_ok=True)

    # 1. Extract text + region + diagram PNG.
    run([
        "uv", "run", "python", "scripts/study_extractor.py",
        "--pdf", str(PDF),
        "--study", str(study_number),
        "--out", str(out),
    ], cwd=ROOT)

    region = json.loads((out / "region.json").read_text())

    # 2a. A gbr_override.txt sidecar corrects a GBR code the book itself
    # mis-prints (e.g. study 211's "0044.01" for a two-white-bishop ending,
    # which should read "0024.01"). It feeds both the classifier's material
    # correction and the value stored in the study JSON.
    gbr_override_file = out / "gbr_override.txt"
    gbr_override = (
        gbr_override_file.read_text().strip() if gbr_override_file.exists() else None
    )

    # 2b. Decide FEN: CLI override > sidecar file > classifier.
    # Overrides are trusted ground truth, so their FEN is assumed sound.
    classifier_kings_ok = True
    classifier_material_ok = True
    override_file = out / "fen_override.txt"
    if fen_override:
        fen = fen_override
        source = "cli"
    elif override_file.exists():
        fen = override_file.read_text().strip()
        source = "override_file"
    else:
        # Classifier needs the GBR string from the study's text so it
        # can apply the king-square correction. Pull the first GBR-
        # shaped line out of text.txt (unless overridden above).
        if gbr_override:
            gbr = gbr_override
        else:
            text = (out / "text.txt").read_text()
            import re
            m = re.search(r"(\d{4}\.\d{2}(?:\s+[a-h][1-8][a-h][1-8])?)", text)
            gbr = m.group(1) if m else ""
        cres = run([
            "uv", "run", "python", "scripts/classify_position.py",
            "--diagram", str(out / "diagram_region.png"),
            "--gbr", gbr,
        ], cwd=ROOT)
        classification = json.loads(cres.stdout)
        fen = classification["fen"]
        source = "classifier"
        classifier_kings_ok = classification.get("kings_ok", True)
        classifier_material_ok = classification.get("material_ok", True)
        if classification.get("warnings"):
            for w in classification["warnings"]:
                print(f"[{study_number}] {w}", file=sys.stderr)

        # Officer-type transpositions (rook/bishop, queen/bishop, knight/rook)
        # keep the GBR material counts intact, so the material correction is
        # blind to them. The solution is not: only the true placement makes the
        # book's moves legal. Try GBR-consistent type assignments and adopt one
        # only if it parses strictly deeper than the classifier's own guess.
        res = resolve_types(
            fen,
            (out / "text.txt").read_text(),
            region,
            decode_gbr_material(gbr),
        )
        if res["changed"]:
            print(f"[{study_number}] {res['reason']}", file=sys.stderr)
            print(f"[{study_number}]   {fen}  ->  {res['fen']}", file=sys.stderr)
            fen = res["fen"]
            source = "classifier+solution"

    # 3. Parse moves.
    STUDY_CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    # A forced rebuild of a study that was previously curated keeps its marker,
    # so it stays protected from the next non-forced rebuild.
    was_curated = json_path.exists() and (
        json.loads(json_path.read_text()).get("curated") is True
    )
    run([
        "uv", "run", "python", "scripts/parse_study.py",
        "--text", str(out / "text.txt"),
        "--region", str(out / "region.json"),
        "--fen", fen,
        "--out", str(json_path),
    ], cwd=ROOT)

    # parse_study re-derives the GBR from the text, so re-apply the override
    # to the stored study after the fact. Also re-stamp the curated marker and
    # the FEN-override flag so the rebuilt JSON stays self-describing.
    parsed = json.loads(json_path.read_text())
    dirty = False
    if gbr_override and parsed.get("gbr") != gbr_override:
        parsed["gbr"] = gbr_override
        dirty = True
    if (was_curated or fen_override or override_file.exists() or gbr_override) and not parsed.get("curated"):
        parsed["curated"] = True
        dirty = True
    if dirty:
        json_path.write_text(
            json.dumps(parsed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    return {
        "study": study_number,
        "chapter": region["chapter_num"],
        "source": source,
        "moves": len(parsed["moves"]),
        "fen": fen,
        "kings_ok": classifier_kings_ok,
        "material_ok": classifier_material_ok,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, help="single study number to build")
    ap.add_argument("--fen", type=str, help="starting FEN override")
    ap.add_argument("--all", action="store_true",
                    help="build every detected study (slow; writes to "
                         "src/content/studies/ in bulk)")
    ap.add_argument("--limit", type=int, help="with --all, cap the run at N studies")
    ap.add_argument("--force", action="store_true",
                    help="rebuild even curated (hand-built/override) studies, "
                         "overwriting their committed JSON")
    args = ap.parse_args()

    if args.study is not None:
        result = build_one(args.study, args.fen, force=args.force or args.fen is not None)
        print(json.dumps(result, indent=2))
        return

    if not args.all:
        ap.error("--study or --all required")

    regions = list_studies(PDF)
    if args.limit:
        regions = regions[: args.limit]
    summary: list[dict] = []
    for r in regions:
        try:
            s = build_one(r.number, None, force=args.force)
            summary.append(s)
            if s.get("skipped"):
                print(f"⏭  study {r.number:3d}  ch {r.chapter_num}  curated — skipped")
            else:
                print(f"✓ study {r.number:3d}  ch {r.chapter_num}  "
                      f"{s['moves']:3d} moves  ({s['source']})")
        except subprocess.CalledProcessError as e:
            print(f"✗ study {r.number:3d}  FAILED: {e.stderr.strip()[:200]}",
                  file=sys.stderr)
            summary.append({"study": r.number, "error": str(e)})

    (ROOT / "data" / "build_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    built = sum(1 for s in summary if "error" not in s and not s.get("skipped"))
    skipped = sum(1 for s in summary if s.get("skipped"))
    print(f"\n{built} built, {skipped} curated-skipped, "
          f"{len(summary) - built - skipped} failed (of {len(summary)})")


if __name__ == "__main__":
    main()
