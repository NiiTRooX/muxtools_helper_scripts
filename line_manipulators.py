# functions meant to be used with manipulate_lines()
from muxtools.subtitle.sub import LINES
from muxtools.subtitle.basesub import _Line
from collections.abc import Callable
import re


__all__ = ["unfuck_bd_dx", "remove_credits", "strip_weird_unicode", "replace_font_for_glyphs", "fix_missing_glyphs", "replace_substr", "replace_style"]


def _replace_style_with_tag(line:_Line, style:str, tag:str, exact:bool, default_style:str="Default") -> None:
    """
    Prepends a formatting tag to the text of a line when its style matches the given style criteria, then resets the line's style to a default value.
    
    Args:
        line (_Line): The line object containing text and style attributes to modify.
        style (str): The style name or substring to match against the line's style.
        tag (str): The tag to prepend to the line's text when a match occurs.
        exact (bool): Whether the style match must be exact (True) or partial (False).
        default_style (str, optional): The style to assign after tagging. Defaults to "Default".
    
    Returns:
        None: The function modifies the `line` object in place.
    """
    if tag[0] != '\\':
        tag = '\\' + tag
    if (exact and style.casefold() == line.style.casefold()) or (not exact and style.casefold() in line.style.casefold()):
        line.text = f"{{{tag}}}{line.text}"
        line.style = default_style


def unfuck_bd_dx(lines:LINES) -> LINES:
    """
    Changes the styles of BD DX, BD Top DX, etc. to Default and Signs and adds the needed tags.
    
    Make sure the styles "Default" and "Signs" exist.
    
    Subs that use this style can be already fucked up (sometimes CR converts them to use Default style without adding an tags, sometimes script_res is 360p, sometimes 1080p and pos values don't have to match the resolution).
    """
    default_style = "Default"
    signs_style = "Signs"
    an1_style = "Bottom Left"
    an2_style = "BD DX"  # Default
    an3_style = "Bottom Right"
    an4_style = "Center Left"
    an5_style = "BD Center"  # has to be exact, or compare last
    an6_style = "Center Right"
    an7_style = "Top Left"
    an8_style = "Top DX"
    an9_style = "Top Right"
    sign_actor = "On-screen"
    for line in lines:
        _replace_style_with_tag(line, style=an1_style, tag=r"\an1", exact=False)
        replace_style(an2_style, default_style)([line])
        _replace_style_with_tag(line, style=an3_style, tag=r"\an3", exact=False)
        _replace_style_with_tag(line, style=an4_style, tag=r"\an4", exact=False)
        _replace_style_with_tag(line, style=an5_style, tag=r"\an5", exact=True)
        _replace_style_with_tag(line, style=an6_style, tag=r"\an6", exact=False)
        _replace_style_with_tag(line, style=an7_style, tag=r"\an7", exact=False)
        _replace_style_with_tag(line, style=an8_style, tag=r"\an8", exact=False)
        _replace_style_with_tag(line, style=an9_style, tag=r"\an9", exact=False)
        if sign_actor.casefold() in line.name.casefold():
            if (line.style.casefold() in [style.casefold() for style in ["Default", default_style, an2_style]]):
                if r"\an" not in line.text.casefold():
                    tags = r"\an2"
                    line.text = f"{{{tags}}}{line.text}"
                line.style = signs_style
    return lines


def remove_credits(lines:LINES) -> LINES|None:
    # Careful with stuff that could delete dialogue
    credits = [
            'Übersetzung:',
            'Spotting:',
            'Revision:',
            'Typesetting:',
            'Qualitätskontrolle:',
            'Projektleitung:',
            "ToonsHub",
            "KawaSubs",
            "Subtitle Timing",
            "Editing & Typesetting",  # some English subtitle credits will be missed if they are in seperate lines
        ]
    removed_lines = []
    for line in lines:
        if any(credit in line.text for credit in credits):
            removed_lines.append(line)
    # removing lines inside the above loop skips the next iteration
    for line in removed_lines:
        lines.remove(line)
    return lines


def strip_weird_unicode(lines:LINES) -> LINES:
    unicode_list = [u"\u200e", u"\u200b", u"\u05B9"]
    replace_list = [(u"\u2011", '-'),
                    (u"\uFF01", "!")]
    for line in lines:
        for unicode in unicode_list:
            line.text = line.text.replace(unicode, "")
        for unicode, replacement in replace_list:
            line.text = line.text.replace(unicode, replacement)
    return lines


def replace_font_for_glyphs(glyphs:list[str], replacement_font:str, styles:list[str]|None=None) -> Callable[[LINES], LINES]:
    r"""
    Replaces the font of glyphs.
    After the glyph the font is set back to the last \fn tag or style default if it's not present.
    
    Returns a function usable with .manipulate_lines().
    
    Args:
        glyphs (list[str]): The glyphs that need a different font.
        replacement_font (str): The font that includes the glyph(s).
        style (list[str] | None): Only replace fonts of a specific style. Set to None to ignore styles.
    """
    if type(glyphs) == str:
        glyphs = list(glyphs)
    fn_pattern = re.compile(r'\\fn([^\\}]+)(?=[\\}])')  # this is supposed to find \fnFont that ends with '\' or '}'. Include this? ')'
    def _replace_font_for_glyph(lines:LINES) -> LINES:
        for line in lines:
            for glyph in glyphs:
                if glyph in line.text:
                    if not styles or (line.style.casefold() in [style.casefold() for style in styles]):
                        replaced_text = ""
                        end_text = ""
                        prev_find = 0
                        for glyph_match in re.finditer(glyph, line.text):
                            pos = glyph_match.start()
                            before = line.text[:pos]
                            fn_matches = fn_pattern.findall(before)
                            last_fn = fn_matches[-1] if fn_matches else ""
                            replaced_text += line.text[prev_find:pos] + fr"{{\fn{replacement_font}}}{glyph}{{\fn{last_fn}}}"
                            end_text = line.text[pos+1:]
                            prev_find = pos + 1
                        line.text = replaced_text + end_text
                        # line.text = line.text.replace(glyph, fr"{{\fn{replacement_font}}}{glyph}{{\fn}}")
        return lines
    return _replace_font_for_glyph


def fix_missing_glyphs(lines:LINES) -> LINES:
    r"""
    Replaces the used font for glyphs that most fonts don't include.
    
    This replaces stuff regardless of style and whether it is commented or not.
    """
    glyphs = [('♪', "Arial"),
              ('・', "Arial Unicode MS"),
              ('）', "Yu Gothic"),  # replace with normal brackets?
              ('（', "Yu Gothic"), # 5mb font, who cares
              ('α', "Arial"),
              ('☆', "Segoe UI Symbol"),
              ('❤', "Segoe UI Symbol"),
              ('「', "Yu Gothic UI Semibold"),
              ('」', "Yu Gothic UI Semibold")
              ]  # add glyphs here
    for glyph, font in glyphs:
        lines = replace_font_for_glyphs(glyphs=glyph, replacement_font=font)(lines)
    return lines


def replace_substr(old:str, new:str, styles:list[str]=None) -> Callable[[LINES], LINES]:
    """
    Replaces every occurence of a string with another.
    Returns a function usable with .manipulate_lines().
    """
    if type(styles) == str:
        styles = [styles]
    
    def _replace_substr(lines:LINES) -> LINES:
        for line in lines:
            if not styles or (line.style.casefold() in styles):
                line.text = line.text.replace(old, new)
        return lines
    return _replace_substr


def replace_style(old:str, new:str) -> Callable[[LINES], LINES]:
    """
    Replaces a every occurence of a style with another.
    Returns a function usable with .manipulate_lines().
    """
    def _replace_style(lines:LINES) -> LINES:
        for line in lines:
            if line.style.casefold() == old.casefold():
                line.style = new
        return lines
    return _replace_style
