from __future__ import annotations

import subprocess
from os import PathLike


def run_cmd(cmds: list[str], cwd: str | PathLike | None = None) -> None:
    """Common way want to run and log command for cli"""
    str_c = " ".join([str(c) for c in cmds])
    # flush: the command's own output comes after this line, also when stdout is a pipe
    if cwd:
        print(f"Command run (dir={cwd}): {str_c}", flush=True)
    else:
        print(f"Command run: {str_c}", flush=True)
    subprocess.run(cmds, check=True, cwd=cwd)
