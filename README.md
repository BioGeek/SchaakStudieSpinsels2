# SchaakStudieSpinsels2

Code voor de website [http://schaakstudiespinsels2.be/](http://schaakstudiespinsels2.be/).

Bevat in:
 * data: de brondocumenten met de text van het boek van Bompa
     * `schaakstudiespinsels2.pdf`: dit is de printklare pdf die gebruikt is voor de gedrukte versie op [Lulu](https://www.lulu.com/de/de/shop/ignace-vandecasteele/schaakstudiespinsels-2/paperback/product-14n762rk.html). Dit is dus zeker de meest recente versie van de tekst.
     * `schaakstudiespinsels2.docx`: de meest recente Word versie die ik heb teruggevonden, maar komt niet overeen met de inhoud van de pdf hierboven, dus is een oudere versie
     * `schaakstudiespinsels2_from_pdf.txt`: plain text versie gegenereerd van de pdf
     * `schaakstudiespinsels2_from_docx.txt`: plain text versie gegenereerd van de docx
 * scripts: Python scripts om de text te parsen.
 * content: de tekst opgeplitst per hoofdstul/indspel studie in [Markdown](https://daringfireball.net/projects/markdown/) formaat. Dient als basis voor de [Pelican static site generator](https://docs.getpelican.com/en/stable/)
 * output: de html files die automatisch gegenereerd worden door Pelican op basis van de Markdown files
 * plugins: De plugins die gebruikt worden. Momenteel enkel [pelican_javascript](https://github.com/mortada/pelican_javascript). Is geïnstaleerd als [git submodule](https://github.blog/2016-02-01-working-with-submodules/).
 * themes: Het thema dat ik gekozen heb voor de website: [brutalist](https://github.com/mc-buckets/brutalist). Ik heb [een fork gemaakt met een branch `schaakstudiespinsels`](https://github.com/BioGeek/brutalist/tree/schaakstudiespinsels) waar ik nog wat extra wijzigingen heb aangebracht. Is ook geïnstaleerd als een git submodule.

# Installatie

Zie dat je Python 3.6 of hoger geïnstaleerd hebt.

Clone deze repository. De `--recursive` is nodig omdat ook de content van de submodules te downloaden.

    git clone --recursive https://github.com/BioGeek/SchaakStudieSpinsels2.git 

Ga in de folder:

    cd SchaakStudieSpinsels2

Activeer de submodule

    git submodule update --init --recursive

[Instaleer/update `pip` en maak een virtuele environment aan](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

Op Windows:

    py -m pip install --upgrade pip

Het commando `py -m pip --version` zou minstens versie 20.2.2 moeten weergeven

Maak een virtuele omgeving aan:

    py -m venv env

Activeer de virtuele omgeving

    .\env\Scripts\activate

Instaleer de benodigde packages (oa. [Pelican](https://docs.getpelican.com/en/stable/))

    py -m pip install -r requirements.txt

Test of Pelican werkt

    pelican content

Zou output moeten geven lijkende op:

    Done: Processed 0 articles, 0 drafts, 14 pages, 0 hidden pages and 0 draft pages in 0.16 seconds.    

Draai de site lokaal:

    cd output
    python -m pelican.server

Open nu in een browser [http://localhost:8000/](http://localhost:8000/)

## submodules

Het [brutalist thema is geïnstalleerd als submodule](https://github.com/BioGeek/SchaakStudieSpinsels2/tree/master/themes) van de [`schaakstudiespinsels` branch van mijn fork](https://github.com/BioGeek/brutalist/tree/schaakstudiespinsels).

Als je veranderingen daarin aanbrengt moet je die pushen met:

```
cd themses/brutalist
git add templates/index.html # voorbeeld
git commit -m "Add review qoutes to frontpage" # voorbeeld
git push origin HEAD:schaakstudiespinsels
```

# Publish to Github pages

```
ghp-import --cname=schaakstudiespinsels2.be  output
git push origin gh-pages
```

of, korter:

```
make publish

```

# TODOs

Pelican is een static site generator die paginas in Markdown omvormt naar HTML paginas.

Ik heb de laatste versie  van de pdf naar text omgezet. Hiermee verlies je dus alle formatting. De plain tekst moet opgedeeld worden in 1 Markdown document per eindspelstudie. Idem voor de paar inleidende hoofdstukken.

Ik heb er al een paar gedaan, zie bv [Voorwoord](./content/pages/voorwoord.md) en [Ten geleide](./content/pages/ten_geleide.md). 

Voor de eindspel studies wil ik een interactief Javascript schaakbord hebben dat:
 * begint met de startpositie (afbeelding zoals in boek)
 * met `forward` en `back` controls er onder zodat je de stappen in de begeleidende tekst gevisualiseerd kan zien. De actieve stap die op het bord staat zou dan ook in de tekst gehighlight moeten worden.


Wat we hiervoor waarschijnlijk moeten doen is: 
* elke studie omzetten in [PGN formaat](https://en.wikipedia.org/wiki/Portable_Game_Notation)
* elke de startpositie omzetten in [FEN formaat](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation)

Nog uit te zoeken, welke Javascript library te gebruiken:
* [chessboard.js](https://chessboardjs.com/) + [chess.js](https://github.com/jhlywa/chess.js)
* [Ab-Chess](https://nimzozo.github.io/Ab-Chess/)
* [PgnViewerJS](https://github.com/mliebelt/PgnViewerJS): ziet er veelbelovend uit, maar moet geïnstaleerd worden met `npm` wat niet goed samenwerkt met `Pelican`.

Zien of we de studies kunnen koppelen/laten checken door endgame tablesbases zoals:
 * [Syzygy endgame tablebases](https://syzygy-tables.info/): alle studies tot 7 stukken
     * [lila-tablebase](https://github.com/niklasf/lila-tablebase): public API voor bovenstaande tablebase, accepteert FEN strings
 * [Lomonosov tablebases](http://tb7.chessok.com/): alle studies tot en met 7 stukken, maar is niet gratis
 * [Shredder Endgame Database](http://rgvtxchess.org/page.php?93): alle studies met 3, 4, 5 en 6 (uitgezonderd 5 tegen 1) stukken
 * [Nalimov Endgame Tablebase](http://www.k4it.de/?topic=egtb&lang=en): alle studies tot en met 6 stukken


Potentieel ook interessant:
 * [python-chess](https://python-chess.readthedocs.io/en/latest/index.html): Python library met onder andere move validation
 * [CHESS ENDGAME STUDY DATABASE](https://endgame.md/endgame/): bevat 21 studies van Bompa
* [ARVES](http://www.arves.org/arves/index.php/en/): Alexander Rueb Vereniging voor SchaakEindspelStudie. Bompa was hier [erelid](http://www.arves.org/arves/index.php/en/halloffame/63-vandecasteele-ignace-1926) van.

# Nummering:

    001     Voorwoord
    002     Ten Geleide
    003     Enkele Voor- en Nabeschouwingen
    004     You feel at ease in your command of English
    005     Een Fidele Boel
    006     Manke Maljutka’s (Nu hersteld)
    007     - 1 -
    ... 
    033     - 27 -
    034     Maljutka’s (4 of 5 stukken op het bord)
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

# 3D book cover

Vervang de cover image met:

    <script src="https://3dbook.xyz/books/5f9833d709347300172fa70c/cover.js"></script>

    



