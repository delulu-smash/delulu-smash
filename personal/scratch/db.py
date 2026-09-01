# %%
from __future__ import annotations

from ds.data import init_db

smash_db = init_db()
smash_db.sql("select * from framedata where char_id ='little_mac'")
