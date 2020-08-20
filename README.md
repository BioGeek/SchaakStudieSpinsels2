# SchaakStudieSpinsels2

Bevat in:
 * data: de brondocumenten met de text van het boek van Bompa
     * pdf: dit zijn de pintklare pdfs zoals ze gebruikt zijn op [Lulu](https://www.lulu.com/de/de/shop/ignace-vandecasteele/schaakstudiespinsels-2/paperback/product-14n762rk.html). Dit is dus zeker de meest recente versie.
     * docx: de meest recente versie die ik heb teruggevonden, maar komt niet overeen met de inhoud van de pdf hierboven.
     * txt: plain text versie gegenereerd van de pdf
 * scripts: Python scripts om de text te parsen.

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

Ik heb er al een paar gedaan, zie bv [Voorwoord](./pages/voorwoord.md) en [Ten geleide](./pages/ten_geleide.md). 





