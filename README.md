# SchaakStudieSpinsels2

Code voor de website [http://schaakstudiespinsels2.be/](http://schaakstudiespinsels2.be/), een interactieve begeleider bij het boek *Schaakstudiespinsels 2* van Bompa (Ignace Vandecasteele). Het doel is om het gedrukte boek om te zetten in een website waar je elke eindspelstudie op een speelbaar schaakbord kan doorlopen, met de volledige variantenboom.

De gedrukte versie is te koop op [Lulu](https://www.lulu.com/de/de/shop/ignace-vandecasteele/schaakstudiespinsels-2/paperback/product-14n762rk.html).

## Twee delen

Het project bestaat uit twee grotendeels onafhankelijke onderdelen:

1. **Astro-site** (`src/`) — de eigenlijke website. Statisch gegenereerd, tweetalig (Nederlands standaard + Engels), met per studie een interactief schaakbord.
2. **Python-pijplijn** (`scripts/`) — leest de gedrukte pdf (`data/schaakstudiespinsels2.pdf`) in en zet elke studie om naar een JSON-bestand dat de Astro-site inleest.

De koppeling tussen beide is het schema in `src/content/config.ts`: de Python-parser produceert exact die vorm en de Astro-componenten lezen ze uit.

## Mappen

 * **`src/`** — de Astro-site.
     * `src/content/pages/<taal>/` — de inleidende hoofdstukken als Markdown/MDX.
     * `src/content/studies/NNN.json` — één bestand per eindspelstudie (door de Python-pijplijn gegenereerd).
     * `src/components/StudyBoard.astro` + `src/components/study-board.client.ts` — het interactieve schaakbord ([cm-chessboard](https://github.com/shaack/cm-chessboard) + [chess.js](https://github.com/jhlywa/chess.js)).
     * `src/pages/[locale]/studies/[num].astro` — de pagina van een studie.
     * `src/i18n/` — vertaalstrings en de Nederlands↔Engels-vertaling van zetnotatie.
 * **`scripts/`** — de Python-pijplijn (zie hieronder).
 * **`data/`** — de brondocumenten van het boek van Bompa:
     * `schaakstudiespinsels2.pdf` — de printklare pdf die voor de gedrukte versie gebruikt is; de meest recente versie van de tekst. (Niet in git — lokaal aangeleverd.)
     * `template.png` — een strook met Bompa's zes stuk-silhouetten, gebruikt voor stukherkenning én voor het genereren van de bord-sprite.
     * `schaakstudiespinsels2.docx` — een oudere Word-versie die niet overeenkomt met de pdf.
     * `schaakstudiespinsels2_from_pdf.txt` / `_from_docx.txt` — plain-textexports.

## Installatie

Clone de repository:

    git clone https://github.com/BioGeek/SchaakStudieSpinsels2.git
    cd SchaakStudieSpinsels2

### Site (Astro / npm)

```bash
npm install        # installeer JS-dependencies
npm run dev        # dev-server met live reload
npm run build      # statische build -> dist/
npm run preview    # serveer de gebouwde dist/
```

### Python-pijplijn (Python 3.12, beheerd met uv)

[uv](https://docs.astral.sh/uv/) beheert de Python-omgeving (zie `pyproject.toml`, `uv.lock`, `.python-version`).

```bash
uv sync                                            # dependencies in .venv
uv run python scripts/study_extractor.py --list    # lijst alle studies + hun plaats in de pdf
uv run python scripts/build_study.py --study 152   # bouw één studie -> src/content/studies/152.json
uv run python scripts/build_study.py --all         # herbouw elke gedetecteerde studie (traag)
```

De pijplijn heeft `data/schaakstudiespinsels2.pdf` en `data/template.png` nodig.

## De Python-pijplijn

`build_study.py` is de orkestrator en koppelt drie scripts aan elkaar (samen vervangen ze het oudere, monolithische `pdf_processing.py`):

1. **`study_extractor.py`** — vindt studie-grenzen door op elke pagina de `- N -`-kopjes te zoeken en ze in leesvolgorde te sorteren (linkerkolom van boven naar onder, dan rechterkolom). Schrijft per studie `text.txt`, `region.json` en een diagram-PNG naar `data/exemplar/<N>/`.
2. **`classify_position.py`** — leidt de begin-FEN af uit het diagram: vormherkenning via Hu-momenten voor het *type* stuk, gemiddelde helderheid in het stuk-masker voor de *kleur*. Controleert de koningsvelden tegen de GBR-index van het boek. Bekende zwakte: dame versus toren onderscheiden.
3. **`parse_study.py`** — parseert de Nederlandse zetnotatie naar de variantenboom, valideert elke zet met [python-chess](https://python-chess.readthedocs.io/) en bewaart de FEN na elke halfzet.

De FEN kan handmatig overschreven worden: `--fen` op de commandolijn > `data/exemplar/<N>/fen_override.txt` > de classifier.

Op dit moment is ongeveer een kwart van de 317 studies ingelezen.

## Publiceren naar GitHub Pages

Er is nog **geen** geautomatiseerde deploy-flow voor de Astro-site. `npm run build` zet de site in `dist/`; het opzetten van de publicatie is nog werk in uitvoering.

## Notatie en structuur van een studie

Observaties die de parser veronderstelt:
 * Linkerkolom: diagram + GBR-code (bv. `4001.00 d1b3`) + resultaatteken (`+`/`=`) + inleidende tekst + begin van de oplossing.
 * Rechterkolom: vervolg van de oplossing + varianten (A, B, a), b)…).
 * Notatie is Nederlands: K=Koning, D=Dame, T=Toren, L=Loper, P=Paard; pionnen in kleine letters.
 * Varianten vertakken via `Variant A`/`B` (hoofdvarianten) en `a)`, `b)` (subvarianten).
 * Terugverwijzingen als `(zie zet 2.)` verwijzen naar de hoofdlijn.
 * De bronvermelding staat net onder het `- N -`-kopje (bv. "Origineel, 2008", "EBUR, 1999").

## Nuttige bronnen (toekomstig werk)

De studies eventueel koppelen aan / laten controleren door eindspel-tablebases:
 * [Syzygy endgame tablebases](https://syzygy-tables.info/) — alle studies tot 7 stukken; [lila-tablebase](https://github.com/niklasf/lila-tablebase) is een publieke API die FEN-strings aanvaardt.
 * [Lomonosov tablebases](http://tb7.chessok.com/) — tot en met 7 stukken (niet gratis).
 * [Nalimov Endgame Tablebase](http://www.k4it.de/?topic=egtb&lang=en) — tot en met 6 stukken.

Verder interessant:
 * [CHESS ENDGAME STUDY DATABASE](https://endgame.md/endgame/) — bevat 21 studies van Bompa.
 * [ARVES](http://www.arves.org/arves/index.php/en/) — Alexander Rueb Vereniging voor SchaakEindspelStudie; Bompa was [erelid](http://www.arves.org/arves/index.php/en/halloffame/63-vandecasteele-ignace-1926).

## Nummering

De paginavolgorde van het boek (gebruikt voor de `order`-volgorde van de inleidende hoofdstukken en als referentie voor de 308 studies):

    001     Voorwoord
    002     Ten Geleide
    003     Enkele Voor- en Nabeschouwingen
    004     You feel at ease in your command of English
    005     Een Fidele Boel
    006     Manke Maljutka's (Nu hersteld)
    007     - 1 -
    ...
    033     - 27 -
    034     Maljutka's (4 of 5 stukken op het bord)
    035     - 28 -
    ...
    078     - 71 -
    079     Mini - Studies (of Ultra-miniaturen = 6 stukken op het bord)
    080     - 72 -
    ...
    159     - 151 -
    160     Miniaturen (7 stukken op het bord)
    161     - 152 -
    ...
    226     - 217 -
    227     Bijna - Miniaturen (8 stukken op het bord)
    228     - 218 -
    ...
    272     - 262 -
    273     Studies (9 of meer stukken op het bord)
    274     - 263 -
    ...
    319     - 308 -
    320     Het Wilde Westen
    321     De Bermuda Driehoek (Een probleem! Een record?)
    322     Een Vervelende Viervoeter
    323     Index = GBR code
    324     Recensies bij de eerste druk
    325     Colofon

## 3D book cover

Vervang de cover-image met:

    <script src="https://3dbook.xyz/books/5f9833d709347300172fa70c/cover.js"></script>
