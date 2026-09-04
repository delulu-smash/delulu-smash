from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header

from .cell import Cell
from .editor import CodeEditor
from .kernel import Kernel
from .theme import EVERFOREST_DARK


class NotebookApp(App):
    """A tiny Jupyter-like notebook: cells share one persistent kernel."""

    TITLE = "textual-kernel"
    CSS = """
    #cells {
        padding: 1 2;
        scrollbar-size-vertical: 1;
    }
    """
    BINDINGS = [
        Binding("ctrl+enter", "run_cell", "Run cell"),
        Binding("f5", "run_cell", "Run cell", show=False),
        Binding("ctrl+n", "new_cell", "New cell"),
        Binding("ctrl+d", "delete_cell", "Delete cell"),
        Binding("ctrl+j", "cycle_mode", "Cycle cell mode"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.kernel = Kernel()
        self.register_theme(EVERFOREST_DARK)
        self.theme = "everforest-dark"

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(id="cells")
        yield Footer()

    async def on_mount(self) -> None:
        await self.add_cell(focus=True)

    async def add_cell(
        self, *, focus: bool = False, after: Cell | None = None, mode: str = "python"
    ) -> Cell:
        cell = Cell(self.kernel)
        container = self.query_one("#cells", VerticalScroll)
        if after is None:
            await container.mount(cell)
        else:
            await container.mount(cell, after=after)
        if mode != "python":
            await cell.set_mode(mode)
        if focus:
            cell.editor.focus()
            cell.scroll_visible()
        return cell

    def _focused_cell(self) -> Cell | None:
        node = self.focused
        while node is not None and not isinstance(node, Cell):
            node = node.parent
        return node

    async def on_code_editor_submitted(self, _message: CodeEditor.Submitted) -> None:
        """Enter, in a single-line-submit editor (terminal-mode cells) -- run it."""
        await self.action_run_cell()

    async def action_run_cell(self) -> None:
        cell = self._focused_cell()
        if cell is None:
            return
        await cell.run_cell()

        cells = list(self.query(Cell))
        if cell is cells[-1]:
            await self.add_cell(focus=True, mode=cell.mode)
        else:
            next_cell = cells[cells.index(cell) + 1]
            next_cell.editor.focus()
            next_cell.scroll_visible()

    async def action_new_cell(self) -> None:
        focused = self._focused_cell()
        mode = focused.mode if focused is not None else "python"
        await self.add_cell(focus=True, after=focused, mode=mode)

    async def action_cycle_mode(self) -> None:
        cell = self._focused_cell()
        if cell is None:
            return
        await cell.cycle_mode()

    def action_delete_cell(self) -> None:
        cells = list(self.query(Cell))
        if len(cells) <= 1:
            return
        cell = self._focused_cell()
        if cell is None:
            return
        idx = cells.index(cell)
        cell.remove()
        remaining = cells[:idx] + cells[idx + 1 :]
        target = remaining[min(idx, len(remaining) - 1)]
        target.editor.focus()
        target.scroll_visible()


def main() -> None:
    NotebookApp().run()


if __name__ == "__main__":
    main()
