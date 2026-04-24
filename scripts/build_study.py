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

from study_extractor import list_studies

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "data" / "schaakstudiespinsels2.pdf"
EXEMPLAR_DIR = ROOT / "data" / "exemplar"
STUDY_CONTENT_DIR = ROOT / "src" / "content" / "studies"


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a subprocess, forwarding stderr to our own stderr."""
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kwargs)


def build_one(study_number: int, fen_override: str | None) -> dict:
    """Run the extractor + classifier + parser for a single study.

    Returns a small status dict with counts + whether overrides were
    used, so the --all driver can summarise at the end.
    """
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

    # 2. Decide FEN: CLI override > sidecar file > classifier.
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
        # shaped line out of text.txt.
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
        if classification.get("warnings"):
            for w in classification["warnings"]:
                print(f"[{study_number}] {w}", file=sys.stderr)

    # 3. Parse moves.
    json_path = STUDY_CONTENT_DIR / f"{study_number:03d}.json"
    STUDY_CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    run([
        "uv", "run", "python", "scripts/parse_study.py",
        "--text", str(out / "text.txt"),
        "--region", str(out / "region.json"),
        "--fen", fen,
        "--out", str(json_path),
    ], cwd=ROOT)

    parsed = json.loads(json_path.read_text())
    return {
        "study": study_number,
        "chapter": region["chapter_num"],
        "source": source,
        "moves": len(parsed["moves"]),
        "fen": fen,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, help="single study number to build")
    ap.add_argument("--fen", type=str, help="starting FEN override")
    ap.add_argument("--all", action="store_true",
                    help="build every detected study (slow; writes to "
                         "src/content/studies/ in bulk)")
    ap.add_argument("--limit", type=int, help="with --all, cap the run at N studies")
    args = ap.parse_args()

    if args.study is not None:
        result = build_one(args.study, args.fen)
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
            summary.append(build_one(r.number, None))
            print(f"✓ study {r.number:3d}  ch {r.chapter_num}  "
                  f"{summary[-1]['moves']:3d} moves  ({summary[-1]['source']})")
        except subprocess.CalledProcessError as e:
            print(f"✗ study {r.number:3d}  FAILED: {e.stderr.strip()[:200]}",
                  file=sys.stderr)
            summary.append({"study": r.number, "error": str(e)})

    (ROOT / "data" / "build_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    ok = sum(1 for s in summary if "error" not in s)
    print(f"\n{ok}/{len(summary)} studies built successfully")


if __name__ == "__main__":
    main()
