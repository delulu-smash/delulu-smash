-- Keep only your personal keybinding overrides here. Add new bindings or
-- unbind defaults before replacing them.

-- See current bindings and descriptions:
--   omarchy menu keybindings --print

-- To disable every Omarchy default binding, set this in
-- ~/.config/hypr/hyprland.lua before require("default.hypr.omarchy"), then add
-- only the bindings you want below:
--   omarchy_default_bindings = false

-- To disable all preinstalled app/webapp bindings, set:
--   omarchy_preinstalled_bindings = false

-- Add a new binding.
-- o.bind("SUPER + SHIFT + R", "SSH", "alacritty -e ssh your-server")

-- Change an existing binding by unbinding it first, then binding the key again.
-- This example changes SUPER+SPACE from the launcher to the Omarchy root menu.
-- hl.unbind("SUPER + SPACE")
-- o.bind("SUPER + SPACE", "Omarchy menu", "omarchy-menu toggle root")

-- Disable a default binding without replacing it.
-- hl.unbind("SUPER + SHIFT + B")

-- Logitech MX Keys examples:
-- o.bind("SUPER + SHIFT + S", nil, "omarchy-capture-screenshot")
-- o.bind("SUPER + H", nil, "voxtype record toggle")
-- o.bind("SUPER + PERIOD", nil, "omarchy-shell shell toggle omarchy.emojis")

hl.unbind("SUPER + SHIFT + S") -- previously Google Maps
o.bind("SUPER + SHIFT + S", "Screenshot", "omarchy screenshot")
hl.unbind("SUPER + SHIFT + Q") -- previously: Screenrecord
hl.unbind("SUPER + SHIFT + ALT + Q") -- previously: Screenrecord (save)
o.bind("SUPER + SHIFT + Q", "Screenrecord", o.launch(os.getenv("HOME") .. "/repos/delulu-smash/.os/scripts/keybindings/screenrecord.sh"))
o.bind("SUPER + SHIFT + ALT + Q", "Screenrecord (save)", o.launch(os.getenv("HOME") .. "/repos/delulu-smash/.os/scripts/keybindings/screenrecord.sh --save"))
o.bind("SUPER + SHIFT + K", "Discord", o.launch("Discord.desktop"))
hl.unbind("SUPER + SHIFT + V") -- previously: Vscode
o.bind("SUPER + SHIFT + V", "Vscode: delulu-smash", 'code "$HOME/repos/delulu-smash"')

hl.unbind("SUPER + F")
hl.unbind("SUPER + ALT + F")
o.bind("SUPER + F", "Force full width", hl.dsp.window.fullscreen({ mode = "maximized" }))
o.bind("SUPER + ALT + F", "Force fullscreen", hl.dsp.window.fullscreen({ mode = "fullscreen" }))

-- uses spotify widget (instead of desktop app)
-- see https://github.com/stappmus/Omarchy-Spotify for details
-- hl.unbind("SUPER + SHIFT + M") -- previously: Music
-- o.bind("SUPER + SHIFT + M", "Omarchy Spotify","omarchy shell -q quickshell.spotify.player togglePlayer")
o.bind("SUPER + SHIFT + J", "Textual kernel", { tui = os.getenv("HOME") .. "/repos/delulu-smash/.os/scripts/keybindings/textual-kernel.sh", focus = true })
hl.unbind("SUPER + SHIFT + A") -- previously: ChatGPT
o.bind("SUPER + SHIFT + A", "Claude: delulu-smash", { tui = os.getenv("HOME") .. "/repos/delulu-smash/.os/scripts/keybindings/claude-delulu.sh", focus = true })
hl.unbind("SUPER + SHIFT + P") -- previously: Google Photos
o.bind("SUPER + SHIFT + P", "Copy 1Password master password", o.launch(os.getenv("HOME") .. "/repos/delulu-smash/.os/scripts/keybindings/pwd-copy.sh"))
