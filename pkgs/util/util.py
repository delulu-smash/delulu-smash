from __future__ import annotations

from typing import ModuleType


def package_reload(parent_module: ModuleType | str) -> None:
    """
    Reloads and refreshes an imported package (as opposed to just a single module).

    This is particularly useful within Jupyter Notebooks where can ensure changes within file
    are reflected in the current Jupyter session.

    this is needed as to ensure not just reload the parent package module/file but also
    all its underlying sub files/submodules that package may be importing

    ```python
    import smash.util

    import pandas as pd

    smash.util.package_reload(pd)


    import smash.logging
    import smash.util

    smash.util.package_reload(smash)
    ```
    """
    # below inspired from https://stackoverflow.com/questions/35640590/how-do-i-reload-a-python-submodule
    import importlib
    import sys

    if isinstance(parent_module, ModuleType):
        name = parent_module.__name__
    else:
        name = parent_module
    mods = []
    for k, v in sys.modules.items():
        if k.startswith(name):
            mods.append(v)
    for m in mods:
        importlib.reload(m)
