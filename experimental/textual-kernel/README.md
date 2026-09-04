# textual-kernel

PoC: a Jupyter-notebook-like TUI built on [Textual](https://github.com/textualize/textual),
backed by a small in-process "kernel" (`kernel.py`) that keeps a persistent
Python namespace across cell runs — no `ipykernel`/`jupyter_client` involved.

Isolated: its own `pyproject.toml` and venv. Lives under the repo's
`experimental/` dir — git-tracked (unlike the old `local/` scratch dir this
started in), but the folder name is the signal: proof-of-concept, not
production code, delete it whenever it's no longer useful.

## Run

Needs a [Nerd Font](https://www.nerdfonts.com/) installed *and* selected as
your terminal's font, or the cell-mode prompt icons render as tofu/empty
boxes (see [Shell mode](#shell-mode) below for why the app can't set the
second half of that up for you). On macOS:

```sh
brew install --cask font-jetbrains-mono-nerd-font
```

Then point your terminal at the `Mono` variant (`JetBrainsMono Nerd Font
Mono`) in its preferences — e.g. for VSCode's integrated terminal, add
`"terminal.integrated.fontFamily": "JetBrainsMono Nerd Font Mono"` to
`settings.json`.

```sh
cd experimental/textual-kernel
uv sync
uv run textual-kernel
```

## Keybindings

- `Ctrl+Enter` / `F5` — run the focused cell (creates a new cell below, in the
  same mode, if it's the last one). `Ctrl+Enter` needs a terminal that
  reports modified Enter keys (Kitty, iTerm2, WezTerm, Ghostty, etc.) — if
  it does nothing in your terminal, use `F5` instead.
- `Ctrl+N` — insert a new empty cell after the focused one, in the same mode
- `Ctrl+D` — delete the focused cell
- `Ctrl+J` — cycle the focused cell's mode: Python → shell → SQL → Python
  (see [Shell mode](#shell-mode) and [SQL mode](#sql-mode) below)
- `Ctrl+Q` — quit

## Run in a browser

`textual-dev` (dev dependency) provides `textual serve`, which runs the app
as a local web server (WebSocket-based — no code changes needed):

```sh
uv run textual serve "uv run textual-kernel"
# -> http://localhost:8000
```

Textualize also has [`textual-web`](https://github.com/Textualize/textual-web),
a separate tool for publishing an app to a public ephemeral URL through their
relay — not installed here, since it's for sharing over the internet rather
than local use.

## Theme

Everforest (dark, medium contrast) throughout — `theme.py` defines two
separate things, since Textual has two separate theming systems:

- `EVERFOREST_DARK` (`textual.theme.Theme`) drives the app's own UI colors
  (`$primary`, `$accent`, `$panel`, etc, used across all our CSS) — registered
  and activated once in `NotebookApp.__init__`.
- `EVERFOREST_TEXT_AREA` (`textual._text_area_theme.TextAreaTheme`) drives
  the code editor's *syntax* highlighting specifically — a wholly separate
  system, registered per-`CodeEditor` instance in `editor.py`.

Both are ported from the real Everforest sources rather than guessed: the
base palette from `palette.md`, and the syntax colors (`Keyword` → red,
`String`/`Function` → green, `Type` → yellow, `Number`/`Boolean` → purple,
`Constant` → aqua, `Identifier` → blue, `Comment` → grey) from
`colors/everforest.vim`, so the two line up as one consistent look.

## Autocomplete

`editor.py`'s `CodeEditor` adds an IDE-style completion popup on top of
Textual's `TextArea` — mechanics only (when to show it, Tab/Enter/Up/Down
handling); it takes its actual completion source as a callable
(`get_completions`) and doesn't know or care what's behind it. `Cell`
(`cell.py`) is what picks a source based on the cell's mode:

- **Python** — [`jedi`](https://jedi.readthedocs.io/) (`completion.py`) in
  `Interpreter` mode against the live kernel namespace — the same approach
  IPython/Jupyter use, so it completes on variables actually defined by
  earlier cell runs, not just static analysis of the current cell.
- **SQL** — a schema-aware heuristic, no AST; see
  [SQL mode](#sql-mode) below for the full writeup.
- **Shell** — none; disabled entirely (`single_line_submit` short-circuits
  it) since jedi's Python-only completions would be actively wrong there.

(We evaluated `ty` too — see the conversation for the tradeoff — but its
completions are only reachable over the Language Server Protocol, and it's
static-only, so it wouldn't see runtime state from earlier cells without
extra plumbing. `jedi` is a plain in-process function call and fits this
namespace-aware, single-editor use case better.)

- Typing an identifier/attribute character shows the popup live, narrowing
  as you type (driven off `TextArea`'s own `Changed` message, so it reacts
  the same way to typing, backspacing, and pasting).
- `Tab` explicitly (re)opens the popup if it isn't already showing.
- While the popup is open: `Up`/`Down` move the selection, `Tab`/`Enter`
  accept it, `Escape` dismisses it. Normal `TextArea` behavior for those
  keys (indent, newline, unfocus) resumes once it's closed.

## History recall

`Up`/`Down` in an **empty** cell recall previous entries, shell-history
style: `Up` steps to the nearest previous cell's text, `Up` again steps
further back, `Down` comes forward again and, past the newest entry, back
to blank. Only *entering* recall requires the cell to be empty — once
started, `Up`/`Down` keep cycling even though the cell now has text in it
(same as a real shell), and typing anything drops back to normal editing.
A non-empty multi-line cell's `Up`/`Down` are never intercepted — they just
move the cursor, same as any text editor.

The recall pool (`Cell._history_candidates` in `cell.py`) is prior cells'
text **in the same mode only** — a shell cell's `Up` recalls past shell
commands, not Python code or SQL queries — read live off the sibling cells'
current text rather than a separate logged history, so editing a cell above
is immediately reflected the next time recall reaches it.

## Shell mode

One of three cell modes (Python, shell, [SQL](#sql-mode)), cycled with
`Ctrl+J`. Two ways into it:

- **One-off**: start a cell with `!` to run just that run as a shell command
  (IPython-style `!` escape), e.g. `!ls -la` or a multi-line `!` script.
  Works from Python mode only, not SQL mode.
- **`Ctrl+J`**: cycles the whole cell into shell mode persistently — no `!`
  needed on every run, the editor's syntax highlighting switches to bash,
  and the cell's accent bar + prompt turn the distinct shell color
  *immediately*, before you've even run it, so you can tell at a glance
  which cells are which. Pressing `Ctrl+J` twice more cycles through SQL
  mode and back to Python (clearing that cell's prompt/output/run-count on
  each switch, since they belonged to the old interpretation).

  The prompt is a [Nerd Font](https://www.nerdfonts.com/) glyph
  (`Cell.PYTHON_ICON` / `Cell.TERMINAL_ICON` / `Cell.SQL_ICON` in `cell.py`,
  all from the Devicons set: `nf-dev-python` U+E73C, `nf-dev-terminal`
  U+E795, `nf-dev-database` U+E706 — see
  [spec/aesthetics.md](spec/aesthetics.md) for why they're kept to one icon
  set) rather than plain text or emoji — see [Run](#run) above for
  installing one. **Requires the terminal to actually be running a Nerd
  Font**, or these render as tofu/empty boxes — not something the app
  itself can set up, since terminal font is controlled by the terminal
  emulator, entirely outside the app's reach. Installing the font file only
  gets you halfway: each terminal app (VSCode's integrated one, iTerm2,
  Kitty, ...) still needs that font picked in *its own* preferences
  separately.

  If you'd rather not deal with any of this, swap the three constants for
  plain characters or emoji (e.g. `❯` / `!` / `db`, or 🐍 / 💻 / 🗄️) instead.

  Shell-mode cells are also single-line: plain `Enter` runs the cell
  (like `Ctrl+Enter`/`F5`) instead of inserting a newline, shell-prompt
  style — no need to reach for a modifier key for a quick command. The
  jedi completion popup is disabled in this mode too (it doesn't know
  about bash, and typing a shell command would otherwise pop up bogus
  Python completions and steal that same `Enter` keypress to accept one).

Either way, each shell run gets its own subprocess — not a persistent shell
— so `cd` and env var changes don't carry over between cells, matching
Jupyter/IPython's own `!` behavior rather than a real integrated shell.

**Bash syntax highlighting**: `theme.py`'s `EVERFOREST_TEXT_AREA.syntax_styles`
was built against Python's tree-sitter captures (`python.scm`); bash's own
query (`bash.scm`) produces a few captures Python's doesn't use —
`property` (variable names), `constant` (command flags like `-la`), and
`embedded` (`$(...)`/`<(...)`/`${...}` substitutions) — which fell back to
plain foreground without an explicit entry, so terminal-mode cells looked
mostly one flat color despite highlighting being active. Added.

**Shell output ANSI colors**: shell stdout/stderr are decoded with Rich's
`Text.from_ansi()` (`cell.py`) before display, so a command run with forced
color (`ls --color=always`, `grep --color=always`, `git -c color.ui=always
status`, ...) renders with its real colors instead of raw escape codes or
plain text.

This only covers commands that *emit* ANSI in the first place. Since our
subprocess is a plain pipe rather than a pty, most tools auto-detect that
and disable their own coloring by default (`isatty()` is false) — same as
piping to `less` or a file. Giving the subprocess a real pty so tools
self-color unprompted was considered too, but rejected here: it merges
stdout/stderr into one stream (losing today's separate error styling),
risks hangs on anything that starts expecting interactive input once it
thinks it has a real terminal, and breaks full-screen programs (`less`,
`vim`, `htop`) that assume cursor-addressable display rather than a
scrollback log.

## SQL mode

The third cell mode, cycled to with `Ctrl+J` (see [Shell mode](#shell-mode)
above). Unlike shell mode, SQL cells stay multi-line — `Enter` inserts a
newline as usual, `Ctrl+Enter`/`F5` runs the query — since real queries
routinely span several lines (`JOIN`s, `WHERE`, `ORDER BY`) and
submit-on-Enter would fight that rather than help it.

A SQL cell shows a small italic connection badge above the editor (e.g.
`sqlite3 · :memory:`) — read straight off the live connection object by
`sql.describe_connection()`, not a hand-maintained label, so it can't drift
out of sync with what `Kernel.sql_connection` actually is. `engine` comes
from the connection class's own module (works for any DBAPI2 driver
unmodified); `target` (what database it's pointed at) has no DBAPI2-wide
standard to read, so `sqlite3` gets a specific case (`PRAGMA
database_list`'s `file` column — the real on-disk path, or empty for an
in-memory connection like today's sample database) and anything else falls
back to the connection's own `repr()`. `Kernel.sql_connection_info()`
exposes this to `Cell.set_mode` (`cell.py`), which reads it fresh whenever
a cell switches into SQL mode — purely informational, not read by
`sql.execute()` itself. Pointing the app at a different connection later
(below) means this updates on its own; a genuinely new driver just needs
its own `target` case added to `describe_connection()` for something more
specific than `repr()`.

Every cell shares one `sqlite3` connection (`Kernel.sql_connection` in
`kernel.py`), seeded on app start (`sql.py`'s `seed_sample_database`) with a
small **in-memory, disposable sample database** — `customers`, `products`,
`orders`, `order_items`, with a two-level foreign key chain
(`order_items` → `orders` → `customers`/`products`) and a mix of `INTEGER`/
`TEXT`/`REAL`/boolean-as-`INTEGER`/date-as-`TEXT`/`NULL` values, enough to
write a real join against. It's reseeded fresh every run — nothing persists
to disk, matching this whole project's disposable, delete-it-later stance.

`sql.py`'s `execute()` is written against the plain DBAPI2 (PEP 249)
connection interface (`cursor()`, `execute()`, `description`, `fetchall()`,
`rowcount`, `commit()`) rather than anything sqlite3-specific — every
mainstream Python SQL driver (`psycopg2`, `mysql-connector-python`,
`duckdb`, ...) implements the same interface, so pointing this at a real
database later means swapping what `Kernel.sql_connection` holds, not
rewriting the execution path.

A query that returns rows comes back as a real `polars.DataFrame` — built
straight from `cursor.description`/`fetchall()` — and renders through the
exact same `dataframe_view` → `DataTable` path a Python cell's own
`polars.DataFrame` output uses (see [Display](#display) below): same
scrolling/zebra-striping/row-cap/`Ctrl+C`-copy behavior, no SQL-specific
display code. A statement with no result set (`INSERT`/`CREATE`/...) prints
its affected-row count instead, mirroring a shell command's stdout. A bad
query's error message renders the same red error box as a Python exception
or a nonzero-exit shell command.

**SQL syntax highlighting**: same story as bash (above) — `sql.scm`'s
tree-sitter captures aren't all shared with `python.scm`, so
`EVERFOREST_TEXT_AREA.syntax_styles` (`theme.py`) needed a few SQL-specific
entries (`field`, `variable`, `parameter`, `attribute`, `storageclass`,
`type.qualifier`) added — mapped by checking `everforest.vim`'s own
`@capture` → `TS*` group → color links directly rather than guessed, same
as every other color choice in this theme.

**SQL autocomplete** (`sql_completion.py`) gets the same live popup as
Python's jedi-backed one (see [Autocomplete](#autocomplete) above) — same
`CompletionPopup`, same Tab/Enter/Up/Down mechanics, same `type` label
rendered next to each suggestion — but with a different completion source
entirely: no SQL AST/parser. General SQL grammars aren't built to parse a
statement *mid-keystroke* the way jedi's parser (`parso`) specifically is,
so instead it's a small heuristic: scan backward from the cursor for the
nearest governing keyword (`FROM`/`JOIN`/`UPDATE`/`INTO` → wants a table
name; `SELECT`/`WHERE`/`ON`/`GROUP BY`/... → wants a column name; anything
else → offers SQL keywords) and, for a `alias.`-qualified prefix, resolve
the alias against every `FROM`/`JOIN` in the whole cell (not just before
the cursor — a `SELECT` list is normally typed *before* its own `FROM`
clause). Either way, the actual candidates are never fabricated or
static — they always come from `Kernel.sql_schema()` → `sql.py`'s
`introspect_schema()`, a live read of the real connected database (SQLite:
`sqlite_master` + `PRAGMA table_info`, one more DBAPI2-driver-specific case
alongside `describe_connection`'s). The heuristic only decides *where to
look* in real schema data, not *what's true* about it — so a wrongly
guessed context shows the wrong *category* of real names, never a made-up
one. `editor.py`'s `CodeEditor` doesn't know or care which source it's
using; `Cell._complete` just dispatches on the cell's current mode.

A few refinements on top of that base heuristic:

- **A misjudged context doesn't hide a keyword.** Typing `F` right after
  `SELECT * ` still has `select` as the nearest governing keyword (the
  heuristic has no notion of "the column list ended at the `*`"), which on
  its own would offer only columns — so keyword matches are always merged
  in whenever something's actually being typed, not just when context
  resolution draws a total blank. `F` there now correctly still suggests
  `FROM`.
- **Space is a trigger character in SQL** (`sql_completion.is_trigger_char`,
  unlike jedi's, which deliberately excludes it) — so the popup shows a
  clean, unfiltered table list the instant you type `FROM `/`JOIN `, not
  only once you've typed a table name's first letter. (Kept out of the
  keyword-merge above: an empty-prefix trigger right after `FROM`/`JOIN`
  stays a focused table list, not that plus all 40 keywords.)
- **`FROM`/`JOIN` table completions auto-suggest an alias**
  (`suggest_alias()`) and insert both together — accepting `customers`
  there inserts `customers c`, ready for `c.` right away. Default is the
  initials of each `_`-separated word (`customers` → `c`, `order_items` →
  `oi`, reducing to a plain first letter for a single-word name), and it
  checks aliases already used elsewhere in the cell to avoid collisions,
  falling back to `c2`, `c3`, ... — visible in the popup itself before you
  even accept (a second `customers` join previews as `customers c2`, not
  `customers c`). Scoped to `FROM`/`JOIN` specifically, not every
  table-context keyword — `UPDATE`/`INSERT INTO`/`ALTER TABLE` name a
  target table in a spot that doesn't take an alias the same way.
- **A column suggestion's `type` label is the table it's from**
  (`customers`, `orders`, ...) instead of a generic `column` — same slot
  a table suggestion uses for `table` and a keyword for `keyword`, just
  filled in with something more specific once there's a real table to
  name. A column that exists on more than one table in scope (`id` on
  both `customers` and `orders` after a join, `name` on both `customers`
  and `products` before any `FROM` is even typed) shows up once *per*
  table rather than merged into one ambiguous entry — `_column_entries()`
  deliberately doesn't deduplicate by column name the way the old
  `_all_columns()` did.
- **Most completions insert a trailing space**, so typing the next token
  never needs its own leading-space keystroke — accepting `SELECT` leaves
  the cursor at `SELECT |`, ready to keep going. Excluded:
  `_NO_TRAILING_SPACE_KEYWORDS` (`COUNT`/`SUM`/`AVG`/`MIN`/`MAX`) — an
  aggregate is always immediately followed by its own `(`, so accepting
  `COUNT` leaves `COUNT|`, ready for `(*)` with no space to delete first.
  That trailing space also reopens the popup immediately for the *next*
  token (`CodeEditor._accept_completion` in `editor.py`, generic across
  both completion sources) — accepting `SELECT` shows column suggestions
  right away rather than going quiet until the next keystroke, so a whole
  `SELECT col FROM table` chain flows as Tab, Tab, Tab. Jedi's completions
  never end in a space, so Python cells are unaffected: accepting there
  stays quiet, same as before.

## Display

Like Jupyter, the value of a trailing bare expression is shown as `Out[n]`.
`display.py` upgrades that for known rich types (a [SQL mode](#sql-mode)
query result is a `polars.DataFrame` by the time it reaches here too, so it
gets the same treatment as one returned from Python code — no separate
code path):

- `polars.DataFrame` / `polars.Series` and `pandas.DataFrame` / `pandas.Series`
  render as a real Textual [`DataTable`](https://textual.textualize.io/widgets/data_table/)
  — scrollable, zebra-striped, capped at 500 rows / 50 columns, with a
  "`n` of `total` rows" caption when truncated. Click/Tab into the table and
  press `Ctrl+C` to copy — via `CopyableDataTable` in `cell.py`, since
  `DataTable` has no `Ctrl+C` of its own. It tries the dataframe's *own*
  native clipboard export first (polars' `write_clipboard()` / pandas'
  `to_clipboard()`), which copies the **full** dataframe (not just the
  capped preview) straight to the real OS clipboard — works in macOS
  Terminal.app, but only for a local session, not over SSH. If that raises
  (no display/clipboard access, e.g. on a headless remote box), it falls
  back to copying just the visible rows as TSV via Textual's
  `App.copy_to_clipboard` (OSC 52), which is the reverse tradeoff: works
  over SSH, but not in macOS Terminal.app. Either way, a small toast
  (`App.notify`) confirms what was copied.
- Anything already Rich-renderable (implements `__rich__` /
  `__rich_console__`, e.g. a `rich.table.Table` you build yourself) is
  passed straight through into a `Static`.
- Everything else falls back to plain `repr()`, same as before.

## Notes / next steps

- Execution is `exec`/`eval` in-process (see `kernel.py`), not a real
  Jupyter kernel — no cross-process isolation, no async/await support at
  the top level, and no image/plot output (matplotlib etc. would need a
  terminal-graphics protocol, which isn't wired up here).
