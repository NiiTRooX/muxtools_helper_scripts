from ass import Style
from muxtools import ASSHeader, SubFile

from .line_manipulators import change_style_for_actor, fix_missing_glyphs, strip_weird_unicode, unfuck_bd_dx
from .line_manipulators import remove_credits as rmv_credits
from .presets import GANDHI_PRESET, SIGNS_PRESET
from .style import get_style

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

    # inefficient
    main2 = get_style(subfile, "main")
    default2 = get_style(subfile, "default")
    bc2 = get_style(subfile, "bottomcenter")
    ot2 = get_style(subfile, "on top")
    sign_actors = ["sign", "On-screen", "title", "Text"]
    if main2:
        main2.name = "signs2"
        subfile.manipulate_lines(change_style_for_actor(sign_actors, old_style="main", new_style="signs2")).restyle(main2, adjust_styles=False)
    if default2:
        default2.name = "signs3"
        subfile.manipulate_lines(change_style_for_actor(sign_actors, old_style="default", new_style="signs3")).restyle(default2, adjust_styles=False)
    if bc2:
        bc2.name = "signs4"
        subfile.manipulate_lines(change_style_for_actor(sign_actors, old_style="bottomcenter", new_style="signs4")).restyle(bc2, adjust_styles=False)
    if ot2:
        ot2.name = "signs5"
        subfile.manipulate_lines(change_style_for_actor(sign_actors, old_style="on top", new_style="signs5")).restyle(ot2, adjust_styles=False)

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
    Wrong \pos values might be Erais fault (Erai was broken and Varyg was fine).
    """
    subfile = subfile\
        .set_headers([ASSHeader.LayoutResX, 640], [ASSHeader.LayoutResY, 360], [ASSHeader.ScaledBorderAndShadow, True], [ASSHeader.YCbCr_Matrix, "TV.709"])\
        .manipulate_lines(unfuck_bd_dx)\
        .unfuck_cr()\
        .manipulate_lines(strip_weird_unicode)\
        .restyle(SIGNS_PRESET)\
        .restyle(styles)
    return subfile