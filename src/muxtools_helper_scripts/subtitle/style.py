from muxtools import SubFile
from ass import Style


__all__ = ["get_style"]


def get_style(subfile:SubFile, style_name:str) -> Style|None:
    doc = subfile._read_doc()
    styles = doc.styles  # what exactly is doc.styles? idk
    for style in styles:
        if style.name == style_name:
            return style
    else:
        # Throw an error instead?
        return None
