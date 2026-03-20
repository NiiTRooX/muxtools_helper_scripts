from muxtools import ParsedFile, PathLike, SubFile, TrackType, ensure_path_exists


__all__ = ["get_sub_track", "all_subs_from_mkv"]


def get_sub_track(file:PathLike, name:str|None=None, lang:str|None=None, is_forced:bool=False, is_default:bool|None=None, preserve_delay:bool=False, quiet:bool=True) -> SubFile:
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
    
    language is 3 letter code (ISO 639-2) and always present.
    
    language_ietf (BCP 47) is the one that can have a dash and might not be present for older stuff.
    
    Example usage:
        ```py
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
