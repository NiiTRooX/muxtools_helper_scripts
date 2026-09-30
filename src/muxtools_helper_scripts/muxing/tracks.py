from shlex import split as split_args

from muxtools import GlobSearch, PathLike, Premux

__all__ = ["video_track2"]


def video_track2(file:PathLike|GlobSearch, name:str="", lang:str="ja", default:bool=True, forced:bool=False, mkvmerge_args:str|list[str]="") -> Premux:
    """
    There seems to be no easy way to get just the videotrack of a file.
    """
    default = "yes" if default else "no"
    forced = "yes" if forced else "no"
    args = f'''--no-global-tags --no-chapters --default-track-flag 0:{default} --forced-display-flag 0:{forced} --language 0:{lang} --track-name 0:"{name}"'''
    args = split_args(args.strip())
    mkvmerge_args = split_args(mkvmerge_args.strip()) if isinstance(mkvmerge_args, str) else mkvmerge_args
    premux = Premux(
        file,
        video=0,
        audio=None,
        subtitles=None,
        keep_attachments=False,
        mkvmerge_args= args + mkvmerge_args
    )
    return premux
