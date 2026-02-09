from muxtools import ParsedFile, SubFile, ASSHeader, Premux, PathLike, GlobSearch, TrackType, ensure_path_exists
from .presets import GANDHI_PRESET, SIGNS_PRESET
from .line_manipulators import unfuck_bd_dx, strip_weird_unicode, fix_missing_glyphs
from .line_manipulators import remove_credits as rmv_credits
from ass import Style


__all__ = ["restyle_cr", "restyle_bd_dx", "get_style", "video_track2", "get_sub_track", "all_subs_from_mkv"]


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
        .unfuck_cr(dialogue_styles=["main", "default", "narrator", "narration", "bottomcenter"], alt_styles=["alt", "overlap"])\
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


def get_sub_track(file:PathLike, name:str|None=None, lang:str|None=None, is_forced:bool=False, is_default:bool|None=None, preserve_delay:bool=False, quiet:bool=True) -> SubFile | None:
    """
    Returns a SubFile object of the first matched track.
    Useful if you dont know the track ID or if it changes between episodes.
    
    :param file: Input mkv file
    :type file: PathLike
    :param name: Name to match, case insensitively and preceeding/leading whitespace removed.
    :type name: str | None
    :param lang: Language to match. This can be any of the possible formats like English/eng/en and is case insensitive.
    :type lang: str | None
    :param is_forced: Forced flag to match.
    :type is_forced: bool
    :param is_default: Default flag to match. Gets ignored if set to None.
    :type is_default: bool | None
    :param preserve_delay: Preserve existing container delay
    :type preserve_delay: bool
    """
    caller = "get_sub_track"
    file = ensure_path_exists(file, caller)
    parsed = ParsedFile.from_file(file, caller)
    if is_default != None:
        condition = lambda track: (track.is_forced == is_forced) and (track.is_default == is_default)
    else:
        condition = lambda track: track.is_forced == is_forced
    parsed_track = parsed.find_tracks(name=name, lang=lang, type=TrackType.SUB, error_if_empty=True, caller=caller, custom_condition=condition)[0]
    if not quiet:
        if parsed_track:
            print(f"Matched subtitle track {parsed_track.relative_index} with title: {parsed_track.title}")
        else:
            print("No matches found")
    return SubFile.from_mkv(file, track=parsed_track.relative_index, preserve_delay=preserve_delay, quiet=quiet)


class SubFileExtended(SubFile):
    title: str | None
    language: str | None
    language_ietf: str | None
    is_default: bool
    is_forced: bool


def all_subs_from_mkv(file:PathLike, preserve_delay: bool = False) -> list[SubFileExtended]:
    """
    WIP
    
    Extract all subtitles with language and title attributes.
    """
    # TODO I'm not happy with the language
    # maybe use language for comparing with standardize_tag()
    # and language_ietf for setting the language tag of the track
    #? is language_ietf always present?
    caller = "all_subs_srom_mkv"
    file = ensure_path_exists(file, caller)
    parsed = ParsedFile.from_file(file, caller)
    parsed_tracks = parsed.find_tracks(type=TrackType.SUB)
    sub_files = []
    for track in parsed_tracks:
        subfile = SubFileExtended.from_mkv(file, track=track.relative_index, preserve_delay=preserve_delay)
        subfile.title = track.title
        # Language object for fancy langcodes stuff
        subfile.language = track.language
        subfile.language_ietf = track.raw_mkvmerge.properties.language_ietf
        subfile.is_default = track.is_default
        subfile.is_forced = track.is_forced
        sub_files.append(subfile)
    return sub_files
