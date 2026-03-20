from muxtools import ParsedFile, SubFile, ASSHeader, Premux, PathLike, GlobSearch, TrackType, ensure_path_exists
from .style import get_style
from .presets import GANDHI_PRESET, SIGNS_PRESET
from .line_manipulators import unfuck_bd_dx, strip_weird_unicode, fix_missing_glyphs, change_style_for_actor
from .line_manipulators import remove_credits as rmv_credits
from ass import Style


__all__ = ["restyle_cr", "restyle_bd_dx"]


def restyle_cr(subfile:SubFile, remove_credits:bool=True, purge_macrons:bool=True, styles:Style|list[Style]=GANDHI_PRESET, replace_glyph_font:bool=False, italicize_narrator:bool=False) -> SubFile:
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

    Returns:
        SubFile: The processed and restyled subtitle file.
    """
    
    # inefficient
    main2 = get_style(subfile, "main")
    default2 = get_style(subfile, "default")
    bc2 = get_style(subfile, "bottomcenter")
    sign_actors = ["sign", "On-screen", "title"]
    if main2:
        main2.name = "signs2"
        subfile.manipulate_lines(change_style_for_actor(sign_actors, old_style="main", new_style="signs2")).restyle(main2, adjust_styles=False)
    if default2:
        default2.name = "signs3"
        subfile.manipulate_lines(change_style_for_actor(sign_actors, old_style="default", new_style="signs3")).restyle(default2, adjust_styles=False)
    if bc2:
        bc2.name = "signs4"
        subfile.manipulate_lines(change_style_for_actor(sign_actors, old_style="bottomcenter", new_style="signs4")).restyle(bc2, adjust_styles=False)
    
    subfile = subfile\
        .set_headers((ASSHeader.LayoutResX, 640), (ASSHeader.LayoutResY, 360), (ASSHeader.ScaledBorderAndShadow, True), (ASSHeader.YCbCr_Matrix, "TV.709"))\
        .manipulate_lines(strip_weird_unicode)
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
    Subs that use this style can be already fucked up (sometimes CR converts them to use Default style without adding \an tags, sometimes script_res is 360p, sometimes 1080p and \pos values don't have to match the resolution).
    """
    subfile = subfile\
        .set_headers([ASSHeader.LayoutResX, 640], [ASSHeader.LayoutResY, 360], [ASSHeader.ScaledBorderAndShadow, True], [ASSHeader.YCbCr_Matrix, "TV.709"])\
        .manipulate_lines(unfuck_bd_dx)\
        .unfuck_cr()\
        .manipulate_lines(strip_weird_unicode)\
        .restyle(SIGNS_PRESET)\
        .restyle(styles)
    return subfile