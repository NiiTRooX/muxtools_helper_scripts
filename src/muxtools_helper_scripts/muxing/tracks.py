from muxtools import GlobSearch, PathLike, Premux


__all__ = ["video_track2"]


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
