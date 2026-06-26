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

`build_study.py` is the orchestrator (`build_one` is the core). For each study it chains four scripts, all of which supersede the older monolithic `pdf_processing.py` (kept only for reference):

1. **`study_extractor.py`** — finds study boundaries by collecting every `- N -` header span across all pages and sorting them in reading order (left column top-to-bottom, then right column). This correctly handles two studies sharing one page, which `pdf_processing.py` silently dropped. Emits `text.txt`, `region.json`, and a diagram PNG into `data/exemplar/<N>/`.
2. **`classify_position.py`** — derives the starting FEN from the diagram image. Two passes: Hu-moment **shape** matching for piece *type* (colour/scale-invariant), then mean-brightness inside the piece mask for *colour*. Piece *locations* are reliable; the *type* is the weak point (similar silhouettes — the classic **queen vs. rook/bishop** confusion). So the GBR code, which specifies exact material, is used as ground truth: `apply_gbr_king_correction` snaps the kings onto their GBR squares, and `apply_gbr_material_correction` relabels mis-typed officers to the type GBR demands (only when unambiguous; count mismatches and ambiguous cases are surfaced as warnings and left for a manual override).
3. **`resolve_types.py`** — repairs classifier piece-type **transpositions** the GBR material correction cannot. A swap of two pieces of different types (rook↔bishop, queen↔bishop, knight↔rook) leaves the material *counts* intact, so `apply_gbr_material_correction` sees nothing wrong — but the swapped board makes the book's first move illegal. The solution is the disambiguator: this stage enumerates every officer-type assignment that keeps the GBR counts (classifier colours and all king/pawn squares fixed), parses the study against each, and adopts the one whose move tree runs **strictly deeper** than the classifier's own guess. Only triggered when the classifier FEN fails to parse the full set of move tokens, so studies the classifier already gets right pay nothing. Source becomes `classifier+solution` when a swap is repaired. This makes type-swap studies reproducible from a clean clone *without* a (gitignored) `fen_override.txt`. It does **not** fix piece-count errors (missing/extra pieces) or king-**colour** swaps — those still need a sidecar override.
4. **`parse_study.py`** — parses the Dutch move notation in `text.txt` into the structured move tree, validating every move through `python-chess` and recording `fenAfter` for each ply. Handles the main line, top-level variants (`Variant A`/`B`), and nested sub-variants (`a)`, `b)`). Prose paragraphs between move blocks become `prose.nl.before`/`after`. A refutation line that opens with a move number (e.g. `3.f8D c1D met remise.`) is split off into prose rather than seeding the move tree; inline alternative-square notation (`Ke(d)3`) is read as its first square (`Ke3`). Inline side-lines embedded mid-mainline are *not* yet clickable — they fall through to prose.

**Verification gate — `verify_studies.py`.** For each study it checks: (1) FEN material + king squares match the GBR code, (2) at least one move parsed, and (3) the **move-tree is consistent** — every move's SAN is legal from its parent's position and lands on its recorded `fenAfter`. Check (3) catches inline-side-line corruption that a move-count check misses. This is the bar for shipping: only studies that pass should be committed to `src/content/studies/`. Run it after any `--all` rebuild (`uv run python scripts/verify_studies.py --fail-only`).

**FEN override precedence** (in `build_study.py`): `--fen` CLI flag > `data/exemplar/<N>/fen_override.txt` sidecar > `resolve_types.py` (solution-driven type repair) > classifier output. Use the sidecar only for what `resolve_types.py` can't repair from the solution — missing/extra pieces (count mismatch) or king/piece **colour** misreads. (Type *swaps* no longer need a sidecar; the solution-driven stage resolves them.) A separate `data/exemplar/<N>/gbr_override.txt` sidecar corrects a GBR code the **book itself mis-prints** (e.g. study 211 printed `0044.01` for a two-white-bishop ending that should read `0024.01`); it feeds both the classifier's material correction and the value stored in the JSON. Note `data/exemplar/` is gitignored — overrides are local regeneration aids; their effect lands in the committed study JSON.

The chapter→page-number table of contents is **hardcoded** as `CHAPTERS` in `study_extractor.py` (six chapters, mirrored in `pdf_processing.py`). If the source PDF is replaced, update those page numbers.

Coverage: **264 of the book's 308 studies are shipped** (`src/content/studies/`); all 264 pass `verify_studies.py`. The old inline-side-line bug (a side variation woven into the move list merged into a variant with a wrong parent link, e.g. study 88's `main.9`) is fixed in `parse_study.py` by two guards: (1) a fresh move-block whose first ply steps *backward* relative to the variant's tail is a reference game or inline side-line, not a continuation, so it is routed to prose instead of merged into the tree (this also un-truncated dozens of studies an early side-line was silently cutting short); and (2) sub-variant labels that *reset* at each branch point (a/b/c after move 2, a fresh a/b after move 5) are made unique (`a`, `a2`, …) so their plies no longer collide into duplicate ids. The ~44 still-unshipped fail for: classifier FEN errors `resolve_types.py` can't repair (count mismatches / colour swaps — need diagram overrides), prose-embedded moves not tabulated, or "same solution as previous study" write-ups. A class of *false-passes* was also fixed — studies whose wrong classifier FEN made the real first move illegal, masked by the old parser seeding the main line from a refutation line; `resolve_types.py` now repairs the type-swap ones, and the rest got sidecar overrides. `data/build_summary.json` records the last `--all` run's per-study status, FEN source, and `kings_ok`/`material_ok` flags.

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
