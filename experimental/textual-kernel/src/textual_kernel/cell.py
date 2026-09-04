from __future__ import annotations

from typing import Any

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import DataTable, Static

from . import completion, sql_completion
from .completion import Completion
from .display import dataframe_view, to_renderable
from .editor import CodeEditor, CompletionPopup
from .kernel import CellResult, Kernel

# Method names, in preference order, for a dataframe's own native clipboard
# export (polars' write_clipboard, pandas' to_clipboard). These write to the
# real OS clipboard directly (no OSC 52), so -- unlike our own TSV fallback
# below -- they work in macOS Terminal.app, at the cost of not working over
# SSH/remote sessions the way OSC 52 does.
_NATIVE_CLIPBOARD_METHODS = ("write_clipboard", "to_clipboard")


class CopyableDataTable(DataTable):
    """``DataTable`` where ``Ctrl+C`` (with the table focused) copies data,
    pasteable straight into a spreadsheet.

    ``DataTable`` has no ``Ctrl+C`` binding of its own -- without this it
    would fall through to the App's own ``Ctrl+C`` (quit-confirmation)
    binding instead of doing nothing useful.
    """

    BINDINGS = [Binding("ctrl+c", "copy_table", "Copy table", show=False)]

    def __init__(self, *, copy_source: Any = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._copy_source = copy_source
        """The original (untruncated) dataframe, if any -- lets Ctrl+C copy
        the real thing via its own native clipboard export rather than just
        the capped/stringified preview this table actually displays."""

    def action_copy_table(self) -> None:
        if self._copy_via_native_method():
            self.app.notify("Copied full dataframe to clipboard", timeout=2)
            return
        self._copy_visible_rows_as_tsv()
        self.app.notify(f"Copied {self.row_count} row(s) to clipboard", timeout=2)

    def _copy_via_native_method(self) -> bool:
        for method_name in _NATIVE_CLIPBOARD_METHODS:
            method = getattr(self._copy_source, method_name, None)
            if method is None:
                continue
            try:
                method()
            except Exception:
                return False
            return True
        return False

    def _copy_visible_rows_as_tsv(self) -> None:
        header = "\t".join(str(column.label) for column in self.ordered_columns)
        rows = (
            "\t".join(str(value) for value in self.get_row_at(index))
            for index in range(self.row_count)
        )
        self.app.copy_to_clipboard("\n".join([header, *rows]))


class Cell(Vertical):
    """One notebook cell: an editable code block plus its output."""

    DEFAULT_CSS = """
    Cell {
        height: auto;
        margin: 0 0 1 0;
        padding: 0 0 0 1;
        border-left: thick $primary-lighten-2;
    }
    Cell:focus-within {
        border-left: thick $accent;
    }
    Cell.-shell {
        border-left: thick $warning;
    }
    Cell.-sql {
        border-left: thick $secondary;
    }
    Cell .prompt {
        width: auto;
        color: $text-muted;
        text-style: bold;
        padding: 0 0 0 1;
    }
    Cell .prompt.-ran {
        color: $primary;
    }
    Cell.-shell .prompt.-ran {
        color: $warning;
    }
    Cell.-sql .prompt.-ran {
        color: $secondary;
    }
    Cell .prompt-row {
        height: auto;
    }
    Cell .connection-info {
        width: auto;
        color: $text-muted;
        text-style: italic;
        margin: 0 0 0 1;
        display: none;
    }
    Cell .connection-info.-visible {
        display: block;
    }
    Cell TextArea, Cell TextArea:focus {
        height: auto;
        max-height: 20;
        border: none;
        padding: 0 1;
        background: transparent;
    }
    Cell .cell-output {
        height: auto;
        padding: 0 1;
        display: none;
    }
    Cell .cell-output.-visible {
        display: block;
    }
    Cell .output-text.-error {
        color: $error;
    }
    Cell .output-caption {
        color: $text-muted;
    }
    Cell DataTable {
        height: auto;
        max-height: 15;
        margin: 0 0 1 0;
        border: none;
    }
    """

    SHELL_PREFIX = "!"
    # Nerd Font glyphs, all from the same Devicons set (nf-dev-*) so the
    # three modes read as one coherent icon family rather than a grab-bag of
    # sets -- see spec/aesthetics.md. Requires the terminal to actually be
    # running a Nerd Font -- see "JetBrainsMono Nerd Font Mono" set up for
    # VSCode's integrated terminal via terminal.integrated.fontFamily in
    # settings.json.
    PYTHON_ICON = ""
    TERMINAL_ICON = ""
    SQL_ICON = ""

    # Cycle order for cycle_mode(): python -> shell -> sql -> python. Shell
    # stays single-line/submit-on-Enter (shell-prompt style, short one-off
    # commands); SQL stays multi-line like Python (queries commonly span
    # several lines -- JOINs, WHERE, ORDER BY -- so submit-on-Enter would be
    # actively hostile there), submitted the same way as Python:
    # Ctrl+Enter/F5.
    MODES = ("python", "shell", "sql")

    def __init__(self, kernel: Kernel, **kwargs) -> None:
        super().__init__(**kwargs)
        self.kernel = kernel
        self.execution_count: int | None = None
        self.mode = "python"
        self._icons = {"python": self.PYTHON_ICON, "shell": self.TERMINAL_ICON, "sql": self.SQL_ICON}
        self._languages = {"python": "python", "shell": "bash", "sql": "sql"}
        self._completion_popup = CompletionPopup()
        self.editor = CodeEditor(
            "",
            language="python",
            soft_wrap=False,
            tab_behavior="indent",
            show_line_numbers=True,
            classes="code-input",
            get_completions=self._complete,
            popup=self._completion_popup,
            is_trigger_char=self._is_trigger_char,
            get_history=self._history_candidates,
        )
        self._prompt = Static(self.PYTHON_ICON, classes="prompt")
        self._connection_info = Static("", classes="connection-info")
        self._output = Vertical(classes="cell-output")

    def compose(self) -> ComposeResult:
        yield Horizontal(self._prompt, self._connection_info, classes="prompt-row")
        yield self.editor
        yield self._completion_popup
        yield self._output

    def _complete(self, source: str, line: int, column: int) -> list[Completion]:
        """The completion source ``CodeEditor`` calls -- dispatches on the
        cell's *current* mode rather than being fixed at construction, so
        switching a cell's mode (``set_mode``) automatically switches what
        Tab/live-typing complete against, no separate rewiring needed.
        """
        if self.mode == "sql":
            return sql_completion.complete(source, line, column, self.kernel.sql_schema())
        return completion.complete(source, line, column, self.kernel.namespace)

    def _is_trigger_char(self, ch: str) -> bool:
        """Same mode-dispatch as ``_complete``, for the same reason: SQL's
        trigger rule (space counts, see ``sql_completion.is_trigger_char``)
        differs from Python's (jedi's, ``completion.is_trigger_char``), and
        it needs to switch the moment a cell's mode does.
        """
        if self.mode == "sql":
            return sql_completion.is_trigger_char(ch)
        return completion.is_trigger_char(ch)

    def _history_candidates(self) -> list[str]:
        """Prior same-mode cell texts, nearest first -- the pool
        ``CodeEditor``'s Up/Down recall (editor.py) draws from. Reads
        straight off the sibling cells' own current text rather than a
        separate history log, so it's always in sync with what's actually
        in the notebook (edit a cell above, and recall reflects that edit).
        """
        if self.parent is None:
            return []
        siblings = [child for child in self.parent.children if isinstance(child, Cell)]
        index = siblings.index(self)
        return [
            sibling.editor.text
            for sibling in reversed(siblings[:index])
            if sibling.mode == self.mode and sibling.editor.text.strip()
        ]

    async def cycle_mode(self) -> None:
        await self.set_mode(self.MODES[(self.MODES.index(self.mode) + 1) % len(self.MODES)])

    async def set_mode(self, mode: str) -> None:
        """Switch to ``mode`` directly (vs. ``cycle_mode``'s always-next-in-list).

        Used by ``cycle_mode`` itself, and by ``NotebookApp`` to carry a
        cell's mode forward onto a newly added cell (Ctrl+Enter's
        auto-added next cell, Ctrl+N) -- new cells otherwise default to
        Python, which is surprising mid-SQL-session/mid-shell-session.
        """
        self.mode = mode
        for m in self.MODES:
            self.set_class(self.mode == m and m != "python", f"-{m}")
        self.editor.language = self._languages[self.mode]
        self.editor.single_line_submit = self.mode == "shell"

        self.execution_count = None
        self._prompt.remove_class("-ran")
        self._prompt.update(self._icons[self.mode])

        if self.mode == "sql":
            engine, target = self.kernel.sql_connection_info()
            self._connection_info.update(f"{engine} · {target}")
            self._connection_info.add_class("-visible")
        else:
            self._connection_info.remove_class("-visible")

        self._completion_popup.hide()
        await self._output.remove_children()
        self._output.set_class(False, "-visible")

    async def run_cell(self) -> None:
        self._completion_popup.hide()

        text = self.editor.text
        if not text.strip():
            return

        if self.mode == "shell":
            await self._run_shell(text)
            return
        if self.mode == "sql":
            await self._run_sql(text)
            return

        stripped = text.lstrip()
        if stripped.startswith(self.SHELL_PREFIX):
            await self._run_shell(stripped[len(self.SHELL_PREFIX) :])
        else:
            await self._run_code(text)

    async def _run_code(self, code: str) -> None:
        self.remove_class("-shell")
        result = self.kernel.run(code)
        await self._finish_run(result, prompt=f"{self.PYTHON_ICON} {result.execution_count}")

    async def _run_shell(self, command: str) -> None:
        self.add_class("-shell")
        result = self.kernel.run_shell(command)
        await self._finish_run(result, prompt=f"{self.TERMINAL_ICON} {result.execution_count}")

    async def _run_sql(self, query: str) -> None:
        result = self.kernel.run_sql(query)
        await self._finish_run(result, prompt=f"{self.SQL_ICON} {result.execution_count}")

    async def _finish_run(self, result: CellResult, *, prompt: str) -> None:
        self.execution_count = result.execution_count
        self._prompt.update(prompt)
        self._prompt.add_class("-ran")

        await self._output.remove_children()
        widgets = self._build_output_widgets(result)
        if widgets:
            await self._output.mount_all(widgets)
        self._output.set_class(bool(widgets), "-visible")

    def _build_output_widgets(self, result: CellResult) -> list[Widget]:
        widgets: list[Widget] = []

        if result.stdout:
            widgets.append(
                Static(Text.from_ansi(result.stdout.rstrip("\n")), classes="output-text")
            )

        if result.result_repr is not None:
            widgets.append(Static(f"Out[{result.execution_count}]:", classes="output-text"))
            view = dataframe_view(result.value)
            if view is not None:
                widgets.extend(self._make_data_table(*view, copy_source=result.value))
            else:
                rich_value = to_renderable(result.value)
                content = rich_value if rich_value is not None else result.result_repr
                widgets.append(Static(content, classes="output-text"))

        if result.stderr:
            widgets.append(
                Static(
                    Text.from_ansi(result.stderr.rstrip("\n"), style="yellow"),
                    classes="output-text",
                )
            )
        if result.error:
            widgets.append(
                Static(
                    Text(result.error.rstrip("\n"), style="bold red"),
                    classes="output-text -error",
                )
            )

        return widgets

    @staticmethod
    def _make_data_table(
        columns: list[str], rows: list[tuple], total_rows: int, *, copy_source: Any = None
    ) -> list[Widget]:
        table = CopyableDataTable(zebra_stripes=True, copy_source=copy_source)
        table.add_columns(*columns)
        table.add_rows(rows)

        widgets: list[Widget] = [table]
        if total_rows > len(rows):
            widgets.append(
                Static(f"({len(rows)} of {total_rows} rows)", classes="output-caption")
            )
        return widgets
