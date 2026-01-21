from muxtools import SubFile, ASSHeader, Premux, PathLike, GlobSearch
from .presets import GANDHI_PRESET, SIGNS_PRESET
from .line_manipulators import unfuck_bd_dx, strip_weird_unicode, fix_missing_glyphs
from .line_manipulators import remove_credits as rmv_credits
from ass import Style


__all__ = ["restyle_cr", "restyle_bd_dx", "get_style", "video_track2"]


def restyle_cr(subfile:SubFile, remove_credits:bool=True, purge_macrons:bool=True, styles:Style|list[Style]=GANDHI_PRESET, replace_glyph_font:bool=False) -> SubFile:
    """
    Normalize and restyle Crunchyroll subtitle files for consistent formatting.

    This function applies a standard set of ASS header values, cleans up common
    Crunchyroll-specific formatting issues, normalizes dialogue text, and
    reapplies one or more target styles. Optional post-processing steps allow
    removal of credit lines, macron stripping, and glyph font substitution for
    missing characters.

    Parameters
    ----------
    subfile : SubFile
        The subtitle file to be processed and restyled.
    remove_credits : bool, optional
        Whether to remove opening/ending credit lines, by default True.
    purge_macrons : bool, optional
        Whether to remove macrons from dialogue text, by default True.
    styles : Style or list[Style], optional
        Style or list of styles to apply to the subtitle file. Defaults to
        `GANDHI_PRESET`.
    replace_glyph_font : bool, optional
        Whether to replace fonts to fix missing glyphs, by default False.

    Returns
    -------
    SubFile
    """
    subfile = subfile\
        .set_headers((ASSHeader.LayoutResX, 640), (ASSHeader.LayoutResY, 360), (ASSHeader.ScaledBorderAndShadow, True), (ASSHeader.YCbCr_Matrix, "TV.709"))\
        .unfuck_cr(dialogue_styles=["main", "default", "narrator", "narration", "bottomcenter"])\
        .manipulate_lines(strip_weird_unicode)\
        .restyle(styles)
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


def get_style(subfile:SubFile, style_name:str) -> Style|None:
    doc = subfile._read_doc()
    styles = doc.styles  # what exactly is doc.styles? idk
    for style in styles:
        if style.name == style_name:
            return style
    else:
        # Throw an error instead?
        return None


def video_track2(file:PathLike|GlobSearch, name:str="", lang:str="ja", default:bool=True, forced:bool=False) -> Premux:
    """
    There seems to be no easy way to get just the videotrack of a file.
    """
    default = "yes" if default else "no"
    forced = "yes" if forced else "no"
    premux = Premux(
        file,
        video=0,
        audio=None,
        subtitles=None,
        keep_attachments=False,
        mkvmerge_args=f'''--no-global-tags --no-chapters --default-track-flag 0:{default} --forced-display-flag 0:{forced} --language 0:{lang} --track-name 0:"{name}"'''
    )
    return premux
