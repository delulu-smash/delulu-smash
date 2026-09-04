"""Everforest (dark, medium contrast) as a Textual theme.

Two separate theming systems, both covered here:

- ``EVERFOREST_DARK`` (``textual.theme.Theme``) drives the app's own UI
  colors ($primary, $accent, $panel, etc, used throughout our CSS).
- ``EVERFOREST_TEXT_AREA`` (``textual._text_area_theme.TextAreaTheme``)
  drives the ``TextArea`` code editor's syntax highlighting -- a completely
  separate system from ``Theme``.

Palette: github.com/sainnhe/everforest/blob/master/palette.md (dark, medium
contrast). Highlight-group colors: github.com/sainnhe/everforest's
``colors/everforest.vim`` (e.g. ``Keyword`` -> red, ``String`` -> green,
``Function`` -> green, ``Type`` -> yellow, ``Number``/``Boolean`` -> purple,
``Constant`` -> aqua, ``Identifier`` -> blue, ``Comment`` -> grey1) -- ported
here rather than guessed, so the two themes read as one consistent palette.
"""

from __future__ import annotations

from rich.style import Style
from textual._text_area_theme import TextAreaTheme
from textual.theme import Theme

# Palette (dark, medium contrast)
_BG0 = "#2D353B"
_BG1 = "#343F44"
_BG2 = "#3D484D"
_BG3 = "#475258"
_BG4 = "#4F585E"
_FG = "#D3C6AA"
_RED = "#E67E80"
_ORANGE = "#E69875"
_YELLOW = "#DBBC7F"
_GREEN = "#A7C080"
_AQUA = "#83C092"
_BLUE = "#7FBBB3"
_PURPLE = "#D699B6"
_GREY1 = "#859289"
_GREY2 = "#9DA9A0"

EVERFOREST_DARK = Theme(
    name="everforest-dark",
    primary=_GREEN,
    secondary=_AQUA,
    accent=_BLUE,
    warning=_YELLOW,
    error=_RED,
    success=_GREEN,
    foreground=_FG,
    background=_BG0,
    surface=_BG1,
    panel=_BG2,
    dark=True,
)

EVERFOREST_TEXT_AREA = TextAreaTheme(
    name="everforest",
    base_style=Style(color=_FG, bgcolor=_BG0),
    gutter_style=Style(color=_GREY1, bgcolor=_BG0),
    cursor_style=Style(color=_BG0, bgcolor=_FG),
    cursor_line_style=Style(bgcolor=_BG1),
    cursor_line_gutter_style=Style(color=_GREY2, bgcolor=_BG1, bold=True),
    bracket_matching_style=Style(bgcolor=_BG3, bold=True),
    selection_style=Style(bgcolor=_BG4),
    syntax_styles={
        "string": Style(color=_GREEN),
        "string.documentation": Style(color=_GREEN, italic=True),
        "comment": Style(color=_GREY1, italic=True),
        "heading.marker": Style(color=_GREY1),
        "keyword": Style(color=_RED, italic=True),
        "operator": Style(color=_ORANGE),
        "repeat": Style(color=_RED, italic=True),
        "exception": Style(color=_RED, italic=True),
        "include": Style(color=_RED, italic=True),
        "keyword.function": Style(color=_RED, italic=True),
        "keyword.return": Style(color=_RED, italic=True),
        "keyword.operator": Style(color=_RED, italic=True),
        "conditional": Style(color=_RED, italic=True),
        "number": Style(color=_PURPLE),
        "float": Style(color=_PURPLE),
        "class": Style(color=_YELLOW),
        "type": Style(color=_YELLOW),
        "type.class": Style(color=_YELLOW),
        "type.builtin": Style(color=_YELLOW),
        "variable.builtin": Style(color=_BLUE),
        # bash.scm captures not shared with python.scm -- without these,
        # a terminal-mode cell's command flags/vars/substitutions fall back
        # to plain foreground and the whole line reads as one flat color.
        "property": Style(color=_BLUE),  # bash variable names ($HOME, etc)
        "constant": Style(color=_AQUA),  # bash command flags (-la, --color)
        "embedded": Style(color=_YELLOW),  # bash $(...) / <(...) / ${...}
        # sql.scm captures not shared with python.scm/bash.scm -- verified
        # against everforest.vim's own @capture -> TS group -> color links
        # (TSField/TSVariable/TSParameter/TSAttribute/TSStorageClass/
        # TSTypeQualifier) rather than guessed, same as the bash entries
        # above.
        "field": Style(color=_BLUE),  # column names (TSField -> Blue)
        "variable": Style(color=_FG),  # table/column aliases (TSVariable -> Fg)
        "parameter": Style(color=_FG),  # bind parameters (TSParameter -> Fg)
        "attribute": Style(color=_PURPLE),  # ASC/NULLS LAST/... (TSAttribute -> Purple)
        "storageclass": Style(color=_ORANGE),  # TEMP/MATERIALIZED/... (TSStorageClass -> Orange)
        "type.qualifier": Style(color=_ORANGE),  # UNIQUE/CASCADE/... (TSTypeQualifier -> Orange)
        "function": Style(color=_GREEN),
        "function.call": Style(color=_GREEN),
        "method": Style(color=_GREEN),
        "method.call": Style(color=_GREEN),
        "boolean": Style(color=_PURPLE, italic=True),
        "constant.builtin": Style(color=_AQUA, italic=True),
        "json.null": Style(color=_AQUA, italic=True),
        "regex.punctuation.bracket": Style(color=_ORANGE),
        "regex.operator": Style(color=_ORANGE),
        "html.end_tag_error": Style(color=_RED, underline=True),
        "tag": Style(color=_RED),
        "yaml.field": Style(color=_BLUE, bold=True),
        "json.label": Style(color=_BLUE, bold=True),
        "toml.type": Style(color=_YELLOW),
        "toml.datetime": Style(color=_PURPLE),
        "css.property": Style(color=_BLUE),
        "heading": Style(color=_RED, bold=True),
        "bold": Style(bold=True),
        "italic": Style(italic=True),
        "strikethrough": Style(strike=True),
        "link.label": Style(color=_BLUE),
        "link.uri": Style(color=_AQUA, underline=True),
        "list.marker": Style(color=_GREY1),
        "inline_code": Style(color=_GREEN),
        "punctuation.bracket": Style(color=_FG),
        "punctuation.delimiter": Style(color=_FG),
        "punctuation.special": Style(color=_ORANGE),
    },
)
