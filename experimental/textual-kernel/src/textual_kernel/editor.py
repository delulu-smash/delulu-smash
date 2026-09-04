"""A TextArea with IDE-style live completion, agnostic to what actually
produces the completions (jedi for Python, the heuristic schema-aware
completer in ``sql_completion.py`` for SQL -- see ``get_completions``).

- Typing an identifier/attribute character shows a completion popup live,
  narrowing as you keep typing (driven off TextArea's own ``Changed``
  message, so it reacts uniformly to typing, backspacing, and pasting).
- Tab explicitly (re)triggers the popup when it isn't already open.
- While the popup is open: Up/Down move the selection, Tab/Enter accept it,
  Escape dismisses it -- normal TextArea behavior for those keys resumes
  once it's closed.
- Up/Down in an *empty* editor recall previous entries from ``get_history``,
  shell-history style (``Up`` = older, ``Down`` = newer, back to blank past
  the newest) -- see ``_handle_history_key``.
"""

from __future__ import annotations

import re
from typing import Callable

from textual import events
from textual.message import Message
from textual.widgets import OptionList, TextArea
from textual.widgets.option_list import Option

from .completion import Completion
from .theme import EVERFOREST_TEXT_AREA


class CompletionPopup(OptionList):
    DEFAULT_CSS = """
    CompletionPopup {
        display: none;
        width: 1fr;
        height: auto;
        max-height: 10;
        overlay: screen;
        constrain: none inside;
        border: tall $border;
        background: $panel;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._completions: list[Completion] = []

    def show_completions(self, completions: list[Completion]) -> None:
        self._completions = completions
        self.clear_options()
        self.add_options(Option(f"{c.name}  [dim]{c.type}[/dim]") for c in completions)
        self.highlighted = 0
        self.display = True

    def hide(self) -> None:
        self.display = False
        self._completions = []

    @property
    def is_open(self) -> bool:
        return self.display

    def current(self) -> Completion | None:
        if not self._completions or self.highlighted is None:
            return None
        return self._completions[self.highlighted]


class CodeEditor(TextArea):
    """``TextArea`` that adds jedi-backed completion on top of the defaults.

    ``popup`` must be mounted by the caller as a *sibling* of this editor
    (in a plain container, not as a child of this widget) -- ``TextArea`` is
    a custom-rendering ``ScrollView``, not a normal layout container, and a
    ``CompletionPopup`` mounted inside one never gets a real size/position
    from the layout engine (it silently collapses to a 0x0 region).

    When ``single_line_submit`` is on, plain ``Enter`` doesn't insert a
    newline -- it posts ``Submitted`` (bubbles up like ``Input.Submitted``)
    instead, for a caller to treat as "run this", shell-prompt style.

    ``get_history`` supplies the Up/Down recall pool on demand (called only
    when recall actually triggers) -- nearest-first order, as many or few
    entries as the caller wants considered "history" for this editor.

    ``get_completions`` is the completion source itself: a callable taking
    ``(source_text, line, column)`` (1-indexed line, 0-indexed column, same
    as ``cursor_location`` -- and the same shape ``completion.complete``
    and ``sql_completion.complete`` both already have) and returning a
    ``list[Completion]``. ``is_trigger_char`` says which just-typed
    characters should proactively (re)show the popup while typing (Tab
    always does, regardless). This editor has no opinion on *what* produces
    completions or *when* they're worth showing unprompted, only on the
    popup/keyboard mechanics around them -- the caller (``Cell``) decides
    which source and trigger rule apply, and can swap both as a cell's mode
    changes.
    """

    class Submitted(Message):
        """Posted when Enter is pressed in single-line-submit mode."""

        def __init__(self, editor: "CodeEditor") -> None:
            self.editor = editor
            super().__init__()

    def __init__(
        self,
        text: str = "",
        *,
        get_completions: Callable[[str, int, int], list[Completion]],
        popup: CompletionPopup,
        is_trigger_char: Callable[[str], bool],
        get_history: Callable[[], list[str]] = list,
        **kwargs,
    ) -> None:
        super().__init__(text, **kwargs)
        self.register_theme(EVERFOREST_TEXT_AREA)
        self.theme = "everforest"
        self._get_completions = get_completions
        self._popup = popup
        self._is_trigger_char = is_trigger_char
        self._get_history = get_history
        self._suppress_next_change = False
        self.single_line_submit = False
        self._history: list[str] = []
        self._history_index: int | None = None

    async def _on_key(self, event: events.Key) -> None:
        popup = self._popup
        if popup.is_open:
            if event.key in ("tab", "enter"):
                event.stop()
                event.prevent_default()
                self._accept_completion()
                return
            if event.key == "escape":
                event.stop()
                event.prevent_default()
                popup.hide()
                return
            if event.key == "up":
                event.stop()
                event.prevent_default()
                popup.action_cursor_up()
                return
            if event.key == "down":
                event.stop()
                event.prevent_default()
                popup.action_cursor_down()
                return

        if event.key in ("up", "down") and self._handle_history_key(event.key):
            event.stop()
            event.prevent_default()
            return

        if event.key == "tab" and not self.single_line_submit and self._prefix_char_before_cursor():
            event.stop()
            event.prevent_default()
            self._update_completions(force=True)
            return

        if event.key == "enter" and self.single_line_submit:
            event.stop()
            event.prevent_default()
            self.post_message(self.Submitted(self))
            return

        await super()._on_key(event)

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        if self._suppress_next_change:
            self._suppress_next_change = False
            return
        self._history_index = None
        self._update_completions()

    def _handle_history_key(self, key: str) -> bool:
        """Up/Down recall, shell-history style. Returns whether it handled
        the key (vs. leaving it to normal cursor movement).

        Only *starts* browsing from an empty editor (the whole point --
        Up/Down must stay plain cursor movement in a non-empty multi-line
        cell), but once started, further Up/Down keep cycling even though
        the editor is no longer empty -- same as a real shell: Up again
        goes further back, Down comes forward, past the newest entry lands
        back on the blank line you started from.
        """
        if self._history_index is None:
            if key != "up" or self.text:
                return False
            history = self._get_history()
            if not history:
                return False
            self._history = history
            self._history_index = 0
            self._set_text_from_history(self._history[0])
            return True

        if key == "up":
            if self._history_index + 1 >= len(self._history):
                return True  # already at the oldest entry -- swallow the key
            self._history_index += 1
        else:
            if self._history_index == 0:
                self._history_index = None
                self._set_text_from_history("")
                return True
            self._history_index -= 1

        self._set_text_from_history(self._history[self._history_index])
        return True

    def _set_text_from_history(self, text: str) -> None:
        self._suppress_next_change = True
        self.text = text
        self.move_cursor(self.document.end)

    def _prefix_char_before_cursor(self) -> str:
        row, column = self.cursor_location
        line = self.document.get_line(row)
        if column <= 0 or column > len(line):
            return ""
        return line[column - 1]

    def _word_before_cursor(self) -> str:
        """The full run of word characters immediately before the cursor
        (vs. ``_prefix_char_before_cursor``'s single char) -- what
        ``_accept_completion`` erases before inserting a completion's full
        text, so acceptance is a clean replace rather than an append.
        """
        row, column = self.cursor_location
        line = self.document.get_line(row)
        match = re.search(r"\w*$", line[:column])
        return match.group(0) if match else ""

    def _update_completions(self, *, force: bool = False) -> None:
        if self.single_line_submit:
            self._popup.hide()
            return

        ch = self._prefix_char_before_cursor()
        if not ch or not (force or self._is_trigger_char(ch)):
            self._popup.hide()
            return

        row, column = self.cursor_location
        completions = self._get_completions(self.text, row + 1, column)
        if completions:
            self._popup.show_completions(completions)
        else:
            self._popup.hide()

    def _accept_completion(self) -> None:
        completion = self._popup.current()
        self._popup.hide()
        if completion is None:
            return

        # Replace the already-typed prefix outright rather than appending
        # a suffix onto it -- a suffix-only insert assumes the completion's
        # text shares the prefix's exact casing, which breaks the moment a
        # source deliberately normalizes case (SQL keywords render/insert
        # uppercase regardless of how they were typed; jedi never hits this
        # since Python identifiers are case-sensitive by construction).
        prefix = self._word_before_cursor()
        row, column = self.cursor_location
        self._suppress_next_change = True
        self.replace(completion.insert, (row, column - len(prefix)), (row, column))

        # A completion that inserts its own trailing space (SQL's, to skip
        # the keystroke for it -- see sql_completion.py) lands the cursor
        # on a fresh trigger boundary for the *next* token, not mid-word --
        # unlike the suppressed change above (which only exists to stop the
        # insert's own text from re-querying completions for itself), this
        # one's worth actively looking at, so typing flows straight into
        # the next round of suggestions instead of going quiet until the
        # next keystroke.
        if completion.insert.endswith(" "):
            self._update_completions()
