from __future__ import annotations

import subprocess


def run_cmd(cmds: list[str], cwd: str | None = None) -> None:
    """Common way want to run and log command for cli"""
    str_c = " ".join([str(c) for c in cmds])
    if cwd:
        print(f"Command run: {str_c}")
    else:
        print(f"Command run (dir={cwd}): {str_c}")
    subprocess.run(cmds, check=True, cwd=cwd)
