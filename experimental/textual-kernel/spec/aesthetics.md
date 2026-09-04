# aesthetics: look and feel

Where `portability.md` is about a visual choice *working at all*, and
`usability.md` is about a binding being *pleasant to use*, this file is
about the UI *reading as one coherent design* rather than a pile of
independently-decided details. Written when SQL mode (a third cell mode
alongside Python and shell) needed an icon and an accent color, and neither
had an obvious answer without writing down the underlying principles first.

## one icon set, not one icon per problem

Every cell-mode prompt glyph (`Cell.PYTHON_ICON` / `TERMINAL_ICON` /
`SQL_ICON` in `cell.py`) is a [Nerd Font](https://www.nerdfonts.com/) glyph
from the same source icon set -- Devicons (`nf-dev-*`): `nf-dev-python`,
`nf-dev-terminal`, `nf-dev-database`. When SQL mode needed a database icon,
Nerd Fonts ships several -- Material Design Icons' `md-database` is more
literally "database-shaped" than Devicons' -- but consistency of set beats
precision of glyph: three icons from three different design languages (three
different stroke widths, corner radii, visual weights) would read as mixed
metaphors even if each one individually looked fine. Pull the next icon from
whatever set the existing ones already came from; only reach for a different
set if that set doesn't have the concept at all.

This is also why these are glyphs and not real inline images (see
`portability.md`'s fonts/glyphs section for why Material Icon Theme's own
SVG assets aren't reachable from a terminal app at all) -- a font is
internally one consistent design regardless of which glyph you pick from it,
which is the property this section actually needs.

Fallback stays a flat, no-taste-required swap: plain characters or emoji
(`❯`/`!`/`db`, or 🐍/💻/🗄️), one constant per mode, same as today.

## one color per mode, from the theme's own roles

Each mode's accent (`Cell.-shell`/`Cell.-sql` border-left + `.prompt.-ran`
color in `cell.py`'s `DEFAULT_CSS`) is one of the roles `EVERFOREST_DARK`
(`theme.py`) already defines for the whole app -- `$primary` (python,
default), `$warning` (shell), `$secondary` (sql) -- never a new literal hex
value reached for just to make one feature look distinct. `$accent` is
reserved separately for focus, and wins over every mode color while a cell
is focused (existing behavior, unchanged by adding a third mode) so "this
cell has focus" stays the one visual fact you can never mistake for
anything else.

Practically: adding a fourth mode later means picking whichever theme role
hasn't been claimed yet ($error and $success remain free), not inventing a
new color. If every role is eventually claimed, that itself is a signal
the mode list has grown past what a single accent-color-per-mode scheme can
distinguish -- worth revisiting the scheme, not just picking a hex value
that happens to look different enough.

## mode identity is visible before you act, not just after

The border/prompt color and the editor's syntax highlighting all switch the
moment a cell's mode changes (`cycle_mode()` in `cell.py`), not only after
the cell is next run -- established for shell mode, held for SQL mode too.
A cell you haven't run yet should never look like the wrong kind of cell.

## shared display, not a bespoke result widget per source

A SQL query's result renders through the exact same `dataframe_view` ->
`CopyableDataTable` path (`display.py`, `cell.py`) as a Python cell
returning a `polars.DataFrame` -- `sql.execute()` (`sql.py`) hands back a
real `polars.DataFrame` specifically so this is true "for free" rather than
needing a second table-rendering code path to keep visually in sync with
the first. One table look, regardless of whether the data came from Python
or a query. New data-producing modes should default to reusing this path
too rather than building their own.

## process

When a new mode/feature needs an icon or a color, check this file's
principles before picking one: same icon set as what's already there, same
finite palette of theme roles, mode identity visible immediately, and reuse
of the existing display pipeline over a new bespoke one. If a genuinely new
kind of visual (not an icon, not an accent color, not tabular data) is
needed, that's the signal to add a new principle here, not just make an
ad hoc choice.
