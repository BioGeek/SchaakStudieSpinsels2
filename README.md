# SchaakStudieSpinsels2

Bevat in:
 * data: de brondocumenten met de text van het boek van Bompa
     * schaakstudiespinsels2.pdf: dit is de printklare pdf die gebruikt is voor de gedrukte versie op [Lulu](https://www.lulu.com/de/de/shop/ignace-vandecasteele/schaakstudiespinsels-2/paperback/product-14n762rk.html). Dit is dus zeker de meest recente versie van de tekst.
     * schaakstudiespinsels2.docx: de meest recente Word versie die ik heb teruggevonden, maar komt niet overeen met de inhoud van de pdf hierboven, dus is een oudere versie
     * schaakstudiespinsels2_from_pdf.txt: plain text versie gegenereerd van de pdf
     * schaakstudiespinsels2_from_docx.txt: plain text versie gegenereerd van de docx
 * scripts: Python scripts om de text te parsen.
 * content: de tekst opgeplitst per hoofdstul/indspel studie in [Markdown](https://daringfireball.net/projects/markdown/) formaat. Dient als basis voor de [Pelican static site generator](https://docs.getpelican.com/en/stable/)
 * output: de html files die automatisch gegenereerd worden door Pelican op basis van de Markdown files

# Installatie

Zie dat je Python 3.6 of hoger geïnstaleerd hebt.

Clone deze repository

    git clone https://github.com/BioGeek/SchaakStudieSpinsels2.git 

Ga in de folder:

    cd SchaakStudieSpinsels2

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









