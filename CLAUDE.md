# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Source for [schaakstudiespinsels2.be](http://schaakstudiespinsels2.be/), an interactive companion to *Schaakstudiespinsels 2* — a book of original chess endgame studies composed by Ignace Vandecasteele ("Bompa", the maintainer's grandfather). The goal is to turn the printed book into a website where each study is a playable, clickable board with its full variation tree.

Two workstreams live here:

1. **Astro site** (`src/`) — the live frontend. Static-rendered, bilingual (Dutch default + English), with an interactive chessboard per study.
2. **Python ingestion pipeline** (`scripts/`) — parses the printed PDF (`data/schaakstudiespinsels2.pdf`) into per-study JSON files that the Astro site consumes.

The contract between the two is `src/content/config.ts` (the Zod `studies` schema) — the Python parser emits exactly that shape, and the Astro components read it.

The primary content language is **Dutch**. Keep prose, Markdown page content, and commit messages in Dutch. Code, identifiers, and docstrings are English.

## Commands

**Site (Astro / npm):**
```bash
npm install            # install JS deps
npm run dev            # live-reload dev server
npm run build          # static build -> dist/
npm run preview        # serve the built dist/
```

**Ingestion pipeline (Python 3.12, managed with uv):**
```bash
uv sync                                          # install Python deps into .venv
uv run python scripts/build_study.py --study 152 # build one study -> src/content/studies/152.json
uv run python scripts/build_study.py --all       # rebuild every detected study (slow)
uv run python scripts/study_extractor.py --list  # list all studies + their PDF locations
```

The pipeline needs `data/schaakstudiespinsels2.pdf` (untracked, provided locally) and `data/template.png` (committed — a strip of Ignace's six piece silhouettes used for classification and sprite generation).

Everything under `data/` except the source documents and `template.png` is gitignored and regenerable (`data/debug/`, `data/endgames/`, `data/exemplar/`, `data/md/`, `data/build_summary.json`).

## Ingestion pipeline architecture (`scripts/`)

`build_study.py` is the orchestrator (`build_one` is the core). For each study it chains three scripts, all of which supersede the older monolithic `pdf_processing.py` (kept only for reference):

1. **`study_extractor.py`** — finds study boundaries by collecting every `- N -` header span across all pages and sorting them in reading order (left column top-to-bottom, then right column). This correctly handles two studies sharing one page, which `pdf_processing.py` silently dropped. Emits `text.txt`, `region.json`, and a diagram PNG into `data/exemplar/<N>/`.
2. **`classify_position.py`** — derives the starting FEN from the diagram image. Two passes: Hu-moment **shape** matching for piece *type* (colour/scale-invariant), then mean-brightness inside the piece mask for *colour*. Validates the two king squares against the book's GBR index line and warns on mismatch. **Known long-tail failure: queen vs. rook** — when it can't tell them apart, override per study.
3. **`parse_study.py`** — parses the Dutch move notation in `text.txt` into the structured move tree, validating every move through `python-chess` and recording `fenAfter` for each ply. Handles the main line, top-level variants (`Variant A`/`B`), and nested sub-variants (`a)`, `b)`). Prose paragraphs between move blocks become `prose.nl.before`/`after`. Inline side-lines embedded mid-mainline are *not* yet clickable — they fall through to prose.

**FEN override precedence** (in `build_study.py`): `--fen` CLI flag > `data/exemplar/<N>/fen_override.txt` sidecar > classifier output. Use the sidecar to permanently fix a study the classifier gets wrong; `--all` skips re-classifying those.

The chapter→page-number table of contents is **hardcoded** as `CHAPTERS` in `study_extractor.py` (six chapters, mirrored in `pdf_processing.py`). If the source PDF is replaced, update those page numbers.

Coverage is partial: ~76 of the book's 317 studies are built so far. `data/build_summary.json` records the last `--all` run's per-study status and FEN source.

## Astro site architecture (`src/`)

- **Content collections** (`src/content/config.ts`):
  - `pages` (type `content`) — MDX/Markdown prose chapters under `src/content/pages/<locale>/`, ordered by an `order` frontmatter field. English pages link back via `translationOf`.
  - `studies` (type `data`) — one JSON per study under `src/content/studies/NNN.json`, matching the schema the Python parser emits.
- **Routing** is file-based with i18n (`astro.config.mjs`: locales `nl`/`en`, default `nl`, `prefixDefaultLocale`):
  - `src/pages/[locale]/[...slug].astro` — renders a prose `pages` entry.
  - `src/pages/[locale]/studies/[num].astro` — renders one study (prose + board). `getStaticPaths` fans out every study × every locale.
  - `src/pages/[locale]/studies/index.astro` — study browser.
  - `src/pages/index.astro` + `src/pages/{nl,en}/index.astro` — root redirect (honoring a stored locale preference) and per-locale home.
- **The board** is split: `StudyBoard.astro` renders the move table server-side (grouping plies into book-style numbered rows and nesting the variant tree); `study-board.client.ts` hydrates it client-side with **cm-chessboard** + **chess.js**, wiring the prev/next/start/end controls and click-to-jump on each move.
- **Move notation**: canonical storage is **English SAN** (what chess.js needs); Dutch display letters (`K D T L P`) are produced by `src/i18n/moves.ts` (`sanToDutch`/`dutchToSan`). UI strings live in `src/i18n/ui.ts`.
- **Piece sprite**: the board uses a custom SVG sprite of Ignace's own piece silhouettes, generated from `data/template.png` by `scripts/generate_piece_sprite.py` into `public/pieces/ignace.svg`.

## Deployment

There is currently **no CI/deploy workflow** and no publish command. `npm run build` produces the static site in `dist/`; wiring up deployment is open work.
