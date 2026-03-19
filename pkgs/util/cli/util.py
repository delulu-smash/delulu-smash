from __future__ import annotations

import subprocess


def run_cmd(cmds: list[str]) -> None:
    """Common way want to run and log command for cli"""
    str_c = " ".join([str(c) for c in cmds])
    print(f"Command run: {str_c}")
    subprocess.run(cmds, check=True)
