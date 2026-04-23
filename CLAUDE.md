# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Source for the Dutch-language website [schaakstudiespinsels2.be](http://schaakstudiespinsels2.be/), a companion to Ignace Vandecasteele's chess-endgame-study book *Schaakstudiespinsels 2*. Two largely independent workstreams live here:

1. **Pelican static site** — Markdown content under `content/pages/` is rendered to HTML and published to GitHub Pages (`gh-pages` branch, CNAME `schaakstudiespinsels2.be`).
2. **Book-ingestion pipeline** — Python scripts + a Jupyter notebook that parse the printed PDF (`data/schaakstudiespinsels2.pdf`) into per-study assets (chess diagram PNG, text column PDF, FEN string) under `data/endgames/`. The eventual goal is to feed those per-study assets into the Pelican site as interactive chess boards — that migration is not yet done; most site pages today are the hand-written introductory chapters only.

The primary content language is Dutch. Keep prose, commit messages to existing code, and Markdown page content in Dutch. Code, identifiers, and docstrings are English.

## Commands

Python is pinned to 3.12 and managed with **uv** (see `pyproject.toml`, `uv.lock`, `.python-version`). The README's `pip install -r requirements.txt` / Python 3.6 instructions are legacy — prefer uv.

```bash
uv sync                         # install dependencies into .venv
uv run pelican content          # build site -> ./output
make html                       # same, via Makefile
make devserver                  # live-reload server on :8000
make publish                    # ghp-import output + push gh-pages (deploys the site)
uv run python scripts/pdf_processing.py   # regenerate data/endgames/ from the PDF
```

The PDF pipeline requires `data/schaakstudiespinsels2.pdf` (untracked, provided locally) and `data/template.png` (committed — a sheet of the six piece glyphs used for OpenCV template matching).

Derived artifacts under `data/` are gitignored (`data/debug/`, `data/endgames/`, `data/md/`). Regenerate the markitdown text export with:

```bash
uvx --from "markitdown[pdf]" markitdown data/schaakstudiespinsels2.pdf -o data/md/schaakstudiespinsels2.md
```

## Submodules — non-obvious

`git clone --recursive` (or `git submodule update --init --recursive`) is **required**; the theme lives in a submodule and the site won't build without it.

- `themes/brutalist` → fork at `BioGeek/brutalist`, branch **`schaakstudiespinsels`** (not `master`). When pushing theme changes: `git push origin HEAD:schaakstudiespinsels`.
- `plugins/pelican_javascript` → upstream `mortada/pelican_javascript`.

## Content conventions (Pelican)

- Pages are ordered via a custom `Pageorder` front-matter field driving `PAGE_ORDER_BY = 'pageorder'` in `pelicanconf.py`. Numbering follows the book's printed sequence (see the full map at the bottom of `README.md`: 001 Voorwoord … 325 Colofon; the 317 endgame studies occupy the bulk of the range). When adding a new page, pick a `Pageorder` that slots it into that sequence.
- The theme expects `SITEIMAGE = 'cover.jpg'` and looks for it in `content/images/`.
- Feed generation is intentionally disabled in `pelicanconf.py` and enabled only in `publishconf.py`.

## PDF pipeline architecture (`scripts/pdf_processing.py`)

Single script orchestrating the whole flow; `main()` is the entry point. Flow to keep in mind when editing:

1. **TOC is hardcoded** (`create_directory_structure`). The six chapters and their starting page numbers are baked in — the script does not parse the book's table of contents. If the source PDF is ever replaced, these page numbers must be updated.
2. **Study boundaries** are found by regex-searching each page's top half for a `- N -` header; each study runs until the next header. Output is keyed by `{chapter_num}_{sanitized_chapter}/endgame{NNN}/`.
3. **Diagram extraction** uses OpenCV template matching against `data/template.png` to read piece positions from each board image, then emits a FEN string to `fen.txt`. The diagram PNG and the study's text columns (extracted as column-clipped PDFs and concatenated) are saved alongside.
4. Page numbers are located and masked out via `find_page_number_region` before text extraction so footers don't pollute the study text.

`parse_endgames.py` / `parse_endgames_from_docx.py` are older, lighter-weight scripts that only enumerate/verify `- N -` headers in the txt/docx exports; they're kept as sanity-check tools, not part of the main pipeline.

## Working with the notebook

`analysis.ipynb` is the live exploration surface for the ingestion pipeline — prefer iterating there before promoting logic into `scripts/pdf_processing.py`. `analysis copy.ipynb` is a scratch duplicate; don't edit it unless asked.
