# usability: ergonomics + convention

Where `portability.md` is about a binding *working at all* across OS/terminal/
host layers, this file is about a working binding being *pleasant and
intuitive to actually use*. A key can pass every portability check and still
be a bad choice if it's awkward to reach or unlike anything the user already
knows.

## reach / ergonomics

- Prefer left-hand keys for frequent or cyclic actions — the right hand is
  more often on the mouse/trackpad or navigating (arrows, Enter), so
  left-hand-only combos can be hit one-handed without leaving that flow.
- Prefer keys at or near home-row finger position for the hand doing the
  reaching (e.g. `G`/`B` are the left index finger's home reach, `S` is the
  left ring finger's home key) over top-row stretches or pinky-corner keys.
- Avoid combos that require both hands to leave a natural typing position at
  once (e.g. a modifier held by one hand plus a key only reachable by
  stretching the other hand across the keyboard).

## combo simplicity

- Prefer a single modifier + one key (`Ctrl+T`) over multi-modifier chords
  (`Ctrl+Shift+X`) or multi-key sequences (`Ctrl+X Ctrl+K`) for anything used
  often. Sequences add a timing/memory burden — fine for rare or destructive
  actions (Claude Code itself reserves `ctrl+x ctrl+k` for killing agents,
  `ctrl+x enter` for queue-submit — not everyday actions), wrong for
  something pressed constantly like a mode toggle.
- Two-key combos (one modifier, one key) are the sweet spot: fast to hit
  repeatedly, low cognitive load, hard to fat-finger.

## laptop-friendly (MacBook Pro baseline)

Assume the primary device is a laptop keyboard, not a full desktop board with
a numpad and dedicated Home/End/PageUp/Down cluster:

- **Function keys aren't free.** On a MacBook, `F1`-`F12` default to media/
  system controls (brightness, volume, Mission Control, ...); getting a literal
  `F5` etc. needs either holding `Fn` on every press or the user changing
  "Use F1, F2, etc. keys as standard function keys" in System Settings. Even
  where an F-key *works* (see `portability.md` on `F5` needing that plus
  being VSCode-intercepted), defaulting to one costs an extra `Fn` press
  most users haven't configured away — a real ergonomic tax, separate from
  whether it technically reaches the app.
- No numpad, and the arrow-key cluster is small/inverted-T — don't lean on
  arrow-key combos for anything that needs precision or speed.
- Trackpad use means the right hand leaves the keyboard often; see the
  left-hand preference above.

## build on existing TUI conventions

A binding that matches what users already know from other tools needs no
memorizing. Check before inventing something new:

- **This app itself is Jupyter-like** (per top-level `README.md`) — Jupyter's
  own conventions (`Shift+Enter` run-and-advance, `Ctrl+Enter` run-in-place,
  modal `Esc` + letter for command-mode actions) are the most directly
  relevant prior art, even though we've chosen a modeless design (direct
  `Ctrl+key` always live, no separate command mode). Worth naming that
  divergence explicitly when it happens, not just picking a different key
  silently.
- **Claude Code** (this repo's other TUI, `~/.claude/keybindings.json`
  defaults) — e.g. `shift+tab` to cycle modes, `ctrl+r` history search,
  `ctrl+o` toggle transcript, `ctrl+c`/`ctrl+d` interrupt/exit. Borrow the
  *feel* where it fits, but a convention only transfers if it also survives
  `portability.md` — e.g. Claude Code's `shift+tab` cycle-mode convention
  does **not** transfer here, because Textual's `Screen` already claims
  `Shift+Tab` for focus navigation (see `portability.md`). Adapt, don't copy
  blindly.
- Other common TUI reference points: vim (modal, `hjkl`, `:`/`/` command and
  search prefixes), tmux (single leader/prefix key, e.g. default `Ctrl+B`,
  followed by a plain letter), nano (`Ctrl+<letter>` shown live in its
  footer — a pattern worth considering here too, since Textual's `Footer`
  widget already shows bindings the same way).

## process

When choosing a new binding, run it through both specs in order:
`portability.md` first (does it work everywhere), then this file (is it
pleasant and familiar). A key that fails portability is disqualified
regardless of how ergonomic it is; a key that passes portability but fails
usability is a candidate for improvement, not a blocker.
