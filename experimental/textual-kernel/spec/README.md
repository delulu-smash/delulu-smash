# spec

Design requirements and constraints for textual-kernel, kept separate from the
top-level `README.md` (which documents what's actually built). One file per
concern, written before or alongside the implementation so intent doesn't only
live in commit messages or our heads.

- [portability.md](portability.md) — OS and terminal-emulator agnosticism:
  keybindings, fonts/glyphs, clipboard.
- [usability.md](usability.md) — ergonomics and convention: reach/hand
  preference, combo simplicity, laptop-keyboard fit, aligning with other TUI
  conventions (Jupyter, Claude Code, vim, tmux, nano).
- [aesthetics.md](aesthetics.md) — look and feel: icon-set consistency,
  per-mode accent colors drawn from the theme's own roles, and reusing one
  shared display pipeline instead of a bespoke widget per feature.

When a spec item is fully satisfied and stable, its content should end up
reflected in the top-level `README.md` too — the spec says what must hold,
the README says what does.
