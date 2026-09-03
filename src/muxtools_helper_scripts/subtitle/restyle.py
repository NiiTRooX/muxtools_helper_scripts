from ass import Style
from muxtools import ASSHeader, SubFile

from .line_manipulators import fix_missing_glyphs, strip_weird_unicode, unfuck_bd_dx
from .line_manipulators import remove_credits as rmv_credits
from .presets import GANDHI_PRESET, SIGNS_PRESET
from .sub import fix_dialog_signs

__all__ = ["restyle_bd_dx", "restyle_cr"]


def restyle_cr(subfile:SubFile, remove_credits:bool=True, purge_macrons:bool=True, styles:Style|list[Style]=GANDHI_PRESET, replace_glyph_font:bool=False, italicize_narrator:bool=False, set_layoutres:bool=True, set_YCbCr_Matrix:bool=True) -> SubFile:
    r"""
    This function applies a standard set of ASS header values, converts top styles into tags, and reapplies one or more target styles.
    Optional post-processing steps allow removal of credit lines, macron stripping, and glyph font substitution for missing characters.

    Args:
        subfile (SubFile): The subtitle file to be processed and restyled.
        remove_credits (bool, optional): Whether to remove translator credits etc. lines. Defaults to True.
        purge_macrons (bool, optional): Whether to remove macrons from dialogue text. Defaults to True.
        styles (Style | list[Style], optional): Style or list of styles to apply to the subtitle file. Defaults to `GANDHI_PRESET`.
        replace_glyph_font (bool, optional): Whether to replace fonts to fix missing glyphs. Defaults to False.
        italicize_narrator (bool, optional): Whether to italize lines that use a narrator style. Defaults to False. If it doesn't match the original narrator style \i tags to emphasize words will be broken.
        set_layoutres (bool): Sets LayoutResX to 640 and LayoutResY to 360.
        set_YCbCr_Matrix (bool): Sets YCbCr Matrix to TV.601 if it's unset otherwise does nothing.

    Returns:
        SubFile: The processed and restyled subtitle file.
    """

    subfile = fix_dialog_signs(subfile, dialog_styles=["main", "default", "bottomcenter", "alt", "overlap", "italic", "internal", "narrat", "on top", "flashback"])

    subfile = subfile.set_headers((ASSHeader.ScaledBorderAndShadow, True)).manipulate_lines(strip_weird_unicode)
    if set_layoutres:
        subfile = subfile.set_headers((ASSHeader.LayoutResX, 640), (ASSHeader.LayoutResY, 360))
    if set_YCbCr_Matrix:
        matrix = "None"
        try:
            matrix = subfile._read_doc().info["YCbCr Matrix"]
        except KeyError:
            pass

        if matrix.casefold() == "none".casefold() or matrix == "":
            subfile = subfile.set_headers((ASSHeader.YCbCr_Matrix, "TV.601"))

    if italicize_narrator:
        subfile = subfile.unfuck_cr(dialogue_styles=["main", "default", "bottomcenter"], alt_styles=["alt", "overlap"], italics_styles=["italics", "internal", "narrator", "narration"])
    else:
        subfile = subfile.unfuck_cr(dialogue_styles=["main", "default", "narrator", "narration", "bottomcenter"], alt_styles=["alt", "overlap"])

    subfile = subfile.restyle(styles)
    if remove_credits:
        subfile = subfile.manipulate_lines(rmv_credits)
    if purge_macrons:
        subfile = subfile.purge_macrons()
    if replace_glyph_font:
        subfile = subfile.manipulate_lines(fix_missing_glyphs)
    return subfile


def restyle_bd_dx(subfile:SubFile, styles:Style|list[Style]=GANDHI_PRESET) -> SubFile:
    r"""    
    Subs that use this style can be already fucked up (sometimes all styles are converted to Default style without adding \an tags, sometimes script_res is 360, sometimes 1080 and \pos values don't have to match the resolution).  
    Wrong \pos values might be the rippers fault or later fixed by CR (Erai was broken and Varyg was fine).
    """
    subfile = subfile\
        .set_headers([ASSHeader.LayoutResX, 640], [ASSHeader.LayoutResY, 360], [ASSHeader.ScaledBorderAndShadow, True])\
        .manipulate_lines(unfuck_bd_dx)\
        .unfuck_cr()\
        .manipulate_lines(strip_weird_unicode)\
        .restyle(SIGNS_PRESET)\
        .restyle(styles)
    matrix = "None"
    try:
        matrix = subfile._read_doc().info["YCbCr Matrix"]
    except KeyError:
        pass

    if matrix.casefold() == "none".casefold() or matrix == "":
        subfile = subfile.set_headers((ASSHeader.YCbCr_Matrix, "TV.601"))
    return subfile
