import re
from typing import Iterator, List, Tuple, Union
import urwid

# ANSI_ESCAPE_REGEX = r"\?\[([\d;]+)m([^\?\[]+)"
ANSI_ESCAPE_REGEX = r"[\x1b\033]\[([\d;]+)m([^\x1b\033]+)"

fg_lookup = {
    30: "black",
    31: "dark red",
    32: "dark green",
    33: "brown",
    34: "dark blue",
    35: "dark magenta",
    36: "dark cyan",
    37: "light gray",
    90: "dark gray",
    91: "light red",
    92: "light green",
    93: "yellow",
    94: "light blue",
    95: "light magenta",
    96: "light cyan",
    97: "white",
}

bg_lookup = {
    40: "black",
    41: "dark red",
    42: "dark green",
    43: "brown",
    44: "dark blue",
    45: "dark magenta",
    46: "dark cyan",
    47: "light gray",
    100: "dark gray",
    101: "light red",
    102: "light green",
    103: "yellow",
    104: "light blue",
    105: "light magenta",
    106: "light cyan",
    107: "white",
}


def translate_color(attr: Union[str, Tuple, List[int]]) -> Tuple[str, str]:
    if isinstance(attr, int):
        list_attr = [attr]
    elif isinstance(attr, (tuple, list)):
        list_attr = attr
    elif isinstance(attr, str):
        list_attr = [int(i) for i in attr.split(";") if len(i) > 0]
    else:
        list_attr = [0]

    fg = ''
    bg = ''

    for elem in list_attr:
        if elem == 0:
            # reset, special case
            fg, bg = '', ''
            continue

        if elem in fg_lookup:
            fg = fg_lookup[elem]
        if elem in bg_lookup:
            bg = bg_lookup[elem]

    return fg, bg


def get_ansii_group_matches_for_text(
        text: str) -> Iterator[Tuple[List[int], str]]:
    for match in re.finditer(ANSI_ESCAPE_REGEX, text, re.DOTALL):
        attr = match.group(1)
        parsed_attr = [int(i) for i in attr.split(";")]
        text = match.group(2)
        yield parsed_attr, text


def translate_text_for_urwid(raw_text):
    if hasattr(raw_text, "decode"):
        raw_text = raw_text.decode("utf-8")

    if '\x1b[0m' == raw_text:
        return []
    formated_text = []

    # Reset the start of text (+ allow for text that isn't formatted)
    if not (raw_text.startswith("\033[") or raw_text.startswith("\x1b[")):
        raw_text = "\x1b[0m" + raw_text

    matches = list(get_ansii_group_matches_for_text(raw_text))
    if not matches:
        if '\x1b[0m' == raw_text:
            return []
        return [raw_text]
    for (attr, text) in matches:
        text = text.replace('?[0m', '')
        if not text:
            continue
        fgcolor, bgcolor = translate_color(attr)
        formated_text.append((urwid.AttrSpec(fgcolor, bgcolor), text))

    return formated_text
