-- Extra autostart processes.
-- o.launch_on_start("my-service")

-- SmashGPT server (delulu-smash experimental/reflex-kernel), so SUPER+SHIFT+I opens instantly.
-- Unit: ~/.config/systemd/user/smashgpt.service
o.exec_on_start("systemctl --user start smashgpt.service")
