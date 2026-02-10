from muxtools.subtitle import get_complimenting_styles, default_style_args
from ass.line import Style
from ass.data import Color


__all__ = ["GANDHI_PRESET", "GANDHI_UW_PRESET", "SIGNS_PRESET", "NOTO_PRESET", "JPN_PRESET", "KOR_PRESET", "SC_PRESET", "TC_PRESET", "THAI_PRESET", "ARAB_PRESET"]


# slightly smaller left and right margins to prevent 3-liners and I don't mind it extending further
gandhi_default = Style(
    name="Default",
    fontname="Gandhi Sans",
    fontsize=75.0,
    outline=3.6,
    shadow=1.5,
    margin_l=150,
    margin_r=150,
    margin_v=55,
    **default_style_args,
)

GANDHI_PRESET = [gandhi_default, *get_complimenting_styles(gandhi_default)]

# smaller font size for ultrawide content on an ultrawide screen
gandhi_uw_default = Style(
    name="Default",
    fontname="Gandhi Sans",
    fontsize=57.0,  # still slightly larger than the normal gandhi preset on 16:9
    outline=2.7,
    shadow=1.125,
    margin_l=220,  # even bigger margins to compensate smaller size?
    margin_r=220,
    margin_v=40,
    **default_style_args,
)

GANDHI_UW_PRESET = [gandhi_uw_default, *get_complimenting_styles(gandhi_uw_default)]

signs_default = Style(
    name="Signs",
    fontname="Arial",
    fontsize=60.0,
    outline=4.0,
    shadow=0.0,
    margin_l=60,
    margin_r=60,
    margin_v=60,
    bold=True,
    italic=False,
    underline=False,
    strike_out=False,
    scale_x=100.0,
    scale_y=100.0,
    spacing=0.0,
    angle=0.0,
    encoding=1,
    alignment=8,
    border_style=1,
    primary_color=Color(r=0xFF, g=0xFF, b=0xFF, a=0x00),
    secondary_color=Color(r=0xFF, g=0x00, b=0x00, a=0x00),
    outline_color=Color(r=0x00, g=0x00, b=0x00, a=0x00),
    back_color=Color(r=0x00, g=0x00, b=0x00, a=0xA0),
)

sign_default = Style(
    name="Sign",
    fontname="Arial",
    fontsize=60.0,
    outline=4.0,
    shadow=0.0,
    margin_l=60,
    margin_r=60,
    margin_v=60,
    bold=True,
    italic=False,
    underline=False,
    strike_out=False,
    scale_x=100.0,
    scale_y=100.0,
    spacing=0.0,
    angle=0.0,
    encoding=1,
    alignment=8,
    border_style=1,
    primary_color=Color(r=0xFF, g=0xFF, b=0xFF, a=0x00),
    secondary_color=Color(r=0xFF, g=0x00, b=0x00, a=0x00),
    outline_color=Color(r=0x00, g=0x00, b=0x00, a=0x00),
    back_color=Color(r=0x00, g=0x00, b=0x00, a=0xA0),
)

SIGNS_PRESET = [signs_default, sign_default]

noto_default = Style(
    name="Default",
    fontname="Noto Sans",
    fontsize=75.0,
    outline=3.6,
    shadow=1.5,
    margin_l=150,
    margin_r=150,
    margin_v=55,
    **default_style_args,
)

NOTO_PRESET = [noto_default, *get_complimenting_styles(noto_default)]

jpn_default = Style(
    name="Default",
    fontname="Noto Sans JP",
    fontsize=75.0,
    outline=3.6,
    shadow=1.5,
    margin_l=150,
    margin_r=150,
    margin_v=55,
    **default_style_args,
)

JPN_PRESET = [jpn_default, *get_complimenting_styles(jpn_default)]

kor_default = Style(
    name="Default",
    fontname="Noto Sans KR",
    fontsize=75.0,
    outline=3.6,
    shadow=1.5,
    margin_l=150,
    margin_r=150,
    margin_v=55,
    **default_style_args,
)

KOR_PRESET = [kor_default, *get_complimenting_styles(kor_default)]

sc_default = Style(
    name="Default",
    fontname="Noto Sans SC",
    fontsize=75.0,
    outline=3.6,
    shadow=1.5,
    margin_l=150,
    margin_r=150,
    margin_v=55,
    **default_style_args,
)

SC_PRESET = [sc_default, *get_complimenting_styles(sc_default)]

tc_default = Style(
    name="Default",
    fontname="Noto Sans TC",
    fontsize=75.0,
    outline=3.6,
    shadow=1.5,
    margin_l=150,
    margin_r=150,
    margin_v=55,
    **default_style_args,
)

TC_PRESET = [tc_default, *get_complimenting_styles(tc_default)]

thai_default = Style(
    name="Default",
    fontname="Noto Sans Thai",
    fontsize=75.0,
    outline=3.6,
    shadow=1.5,
    margin_l=150,
    margin_r=150,
    margin_v=55,
    **default_style_args,
)

THAI_PRESET = [thai_default, *get_complimenting_styles(thai_default)]

arab_default = Style(
    name="Default",
    fontname="Noto Sans Arabic",
    fontsize=75.0,
    outline=3.6,
    shadow=1.5,
    margin_l=150,
    margin_r=150,
    margin_v=55,
    **default_style_args,
)

ARAB_PRESET = [arab_default, *get_complimenting_styles(arab_default)]
