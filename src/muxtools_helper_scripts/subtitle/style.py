from ass import Style
from muxtools import SubFile

__all__ = ["get_style"]


def get_style(subfile:SubFile, style_name:str) -> Style|None:
    doc = subfile._read_doc()
    styles = doc.styles  # what exactly is doc.styles? idk
    for style in styles:
        if style.name.casefold() == style_name.casefold():
            return style
    # Throw an error instead?
    return None
