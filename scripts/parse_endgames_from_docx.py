import re
import docx
from docx import document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

pattern = re.compile('(-\s\d+\s-)')

def iter_block_items(parent):
    """
    Yield each paragraph and table child within *parent*, in document order.
    Each returned value is an instance of either Table or Paragraph. *parent*
    would most commonly be a reference to a main Document object, but
    also works for a _Cell object, which itself can contain paragraphs and tables.
    # See: https://github.com/python-openxml/python-docx/issues/40#issuecomment-436528583
    """
    if isinstance(parent, document.Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("something's not right")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            # yield paragraphs from table cells
            # Note, it works for single level table (not nested tables)
            table = Table(child, parent)
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        yield paragraph

def main(path):
    doc = docx.Document(path)
    for block in iter_block_items(doc):
        text = block.text
        endgames = pattern.findall(text)
        if endgames is not None:
            for endgame in endgames:
                print(endgame)






if __name__ == '__main__':
    path = './data/schaakstudiespinsels2.docx'
    main(path)