import io
import re
from typing import Any

import ass
from ass.line import Style
from muxtools import ParsedFile, PathLike, SubFile, TrackType, ensure_path_exists, info
from muxtools.subtitle.basesub import _Line
from muxtools.subtitle.sub import LINES

from .style import get_style

__all__ = ["all_subs_from_mkv", "detect_sign", "fix_dialog_signs", "get_sub_track", "replace_text_in_subfile"]


def get_sub_track(file:PathLike, name:str|None=None, lang:str|None=None, is_forced:bool=False, is_default:bool|None=None, preserve_delay:bool=False, quiet:bool=True, **kwargs: Any) -> SubFile:
    """
    Return a SubFile object of the first matched track.

    Useful if you do not know the track ID or if it changes between episodes.

    Args:
        file (PathLike): Input MKV file.
        name (str | None): Name to match. Matching is case-insensitive and leading/trailing whitespace is removed.
        lang (str | None): Language to match. Accepts formats such as "English", "eng", or "en". Matching is case-insensitive.
        is_forced (bool): Forced flag to match.
        is_default (bool | None): Default flag to match. Ignored if set to None.
        preserve_delay (bool): Whether to preserve the existing container delay.
        kwargs (Any): Other args to pass to `from_srt` if trying to extract srt subtitles

    Returns:
        SubFile: The first track that matches the given criteria.
    """
    caller = "get_sub_track"
    file = ensure_path_exists(file, caller)
    parsed = ParsedFile.from_file(file, caller)
    if is_default != None:
        condition = lambda track: (track.is_forced == is_forced) and (track.is_default == is_default)
    else:
        condition = lambda track: track.is_forced == is_forced
    parsed_track = parsed.find_tracks(name=name, lang=lang, type=TrackType.SUB, error_if_empty=True, caller=caller, custom_condition=condition)[0]
    if not quiet and parsed_track:
        info(f"Matched subtitle track {parsed_track.relative_index} with title: {parsed_track.title}", get_sub_track)
    return SubFile.from_mkv(file, track=parsed_track.relative_index, preserve_delay=preserve_delay, quiet=quiet, **kwargs)


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
    
    language is 3 letter code (ISO 639-2) and always present.
    
    language_ietf (BCP 47) is the one that can have a dash and might not be present for older stuff.
    
    Example usage:
    ```
        subs = all_subs_from_mkv(file)
        if subs[0].language == "eng":
            pass
        subs[1].to_track(subs[1].title, lang=subs[1].language_ietf)
    ```
    """
    # TODO I'm not happy with the language
    # maybe use language for comparing and language_ietf for setting the language tag of the track
    # language is 3 letter code (ISO 639-2) and always present
    # language_ietf (BCP 47) is the one that can have a dash and might not be present for older stuff
    # matroska spec says 3 letter code should be ignored if ietf is present
    #? standardize_tag() for easier comparisons?
    caller = "all_subs_srom_mkv"
    file = ensure_path_exists(file, caller)
    parsed = ParsedFile.from_file(file, caller)
    parsed_tracks = parsed.find_tracks(type=TrackType.SUB)
    sub_files = []
    for track in parsed_tracks:
        subfile = SubFileExtended.from_mkv(file, track=track.relative_index, preserve_delay=preserve_delay)
        subfile.title = track.title
        # turn into Language object?
        subfile.language = track.language
        subfile.language_ietf = track.raw_mkvmerge.properties.language_ietf
        subfile.is_default = track.is_default
        subfile.is_forced = track.is_forced
        sub_files.append(subfile)
    return sub_files


def replace_text_in_subfile(file:PathLike, old:str, new:str) -> None:
    """
    Useful to fix a malformed header.
    """

    with open(file, "r", encoding="utf-8-sig") as f:
        raw = f.read().replace(old, new)
    
    doc = ass.parse(io.StringIO(raw))

    with open(file, "w", encoding="utf-8-sig") as f:
        doc.dump_file(f)


def fix_dialog_signs(subfile:SubFile, sign_actors = ("sign", "On-screen", "title", "Text"), dialog_styles = ("default", "main", "bottomcenter", "on top"), min_override_tags:int=2) -> SubFile:
    """
    Move signs that were authored using a dialog style onto their own dedicated style,
    without changing how they look.
    """
    if isinstance(sign_actors, str):
        sign_actors = [sign_actors]
    if isinstance(dialog_styles, str):
        dialog_styles = [dialog_styles]

    style_map:dict[str, Style] = {}
    idx = 1
    doc = subfile._read_doc()
    lines:LINES = doc.events
    for line in lines:
        if detect_sign(line, styles=dialog_styles, actors=sign_actors, min_override_tags=min_override_tags):
            style = get_style(subfile, line.style)
            try:
                line.style = style_map[style.name].name
            except KeyError:
                old_style = style.name
                new_style = f"signs{idx}"
                while new_style in [sty.name for sty in doc.styles]:
                    idx += 1
                    new_style = f"signs{idx}"
                style.name = new_style
                style_map[old_style] = style
                line.style = new_style
                doc.styles.extend([style])
    subfile._update_doc(doc)
    return subfile


def detect_sign(line: _Line, styles: list[str] | str | None = None, actors: list[str] | str | None = None, min_override_tags: int = 2) -> bool:
    r"""
    Heuristically detect whether a line is a "sign" (styled/positioned text rather than
    ordinary dialogue), based on its actor name and/or number of override tags.

    A line is considered a sign if either:
      - its actor matches one of `actors`, or
      - it contains at least `min_override_tags` override tags (excluding \b and \i).

    If `styles` is given and the line's style is not among them, the line is skipped
    entirely and this function returns False regardless of the actor/tag checks.

    All name comparisons (style, actor) are case-insensitive.

    Args:
        line: The line to check.
        styles: Style name(s) to restrict the check to. If None, lines of any style
            are checked.
        actors: Actor name(s) that immediately mark a line as a sign, regardless of
            its override tag count. If None, this check is skipped.
        min_override_tags: Minimum number of override tags (not counting \b or \i)
            required for a line to be considered a sign.

    Returns:
        True if the line is considered a sign, False otherwise (including when
        `styles` is given and the line's style doesn't match).
    """
    if isinstance(styles, str):
        styles = [styles]
    if isinstance(actors, str):
        actors = [actors]
    if styles and not (any(style.casefold() in line.style.casefold() for style in styles)):
        return False
    if actors and (line.name.casefold() in [actor.casefold() for actor in actors]):
        return True

    return count_override_tags(line) >= min_override_tags


def count_override_tags(line:_Line, ignore:tuple[str]=('b', 'i')) -> int:
    """
    Count override tags in a line, ignoring the given tag names.
    """
    text = line.text
    count = 0
    for block in re.findall(r'\{([^{}]*)\}', text):
        for name in re.findall(r'\\(\d*[A-Za-z]+)', block):
            base = re.sub(r'\d+$', '', name)  # \b1 -> b, \i0 -> i, etc.
            if base in ignore or name in ignore:
                continue
            count += 1
    return count
