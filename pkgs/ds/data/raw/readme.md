# Sources

Below details how gather raw data below:

_NOTE: this data is untransformed and normalized, just straight copy paste from source_

1. `raw_ko_kill_pct.csv` -> Mac Discord: copy paste from [link](https://docs.google.com/spreadsheets/d/1Fht5zTeF1p6C-79gOIPfZCorS_AIDgmgTezSbnThcAg/edit?gid=0#gid=0)
2. `framedata.py` -> scrapes [ultimateframedata.com](https://ultimateframedata.com) move frame data (`scrape_framedata(character)`, also exposed via `ds ssbu framedata <character>`)
3. `smashmate.py` -> downloads the character stock icons from [nasmashmate.com](https://nasmashmate.com/leaderboard) into `../char_icons/` (`scrape_char_icons(dest)`, exposed via `ds data char_icon`)
4. `supermajor.py` -> [supermajor.gg](https://www.supermajor.gg) player pages (character / stage usage). **Not working since Nov 2026**: the site's bot check blocks player pages. Its tag search (`search_players`) still works and is used to find start.gg player ids
5. `startgg/` -> [start.gg](https://www.start.gg)'s official GraphQL API (`client.py`, `queries.py`, `models.py`, `api.py`): a player's sets and games (characters, stages, results), tournaments, entrants, standings. Needs a token (`ds settings sync`). Check it live with `uv run scripts/startgg_probe.py`

What is computed from start.gg data (player usage, head-to-head, results) is not here but in `../startgg/`.
6. `char_ranking/` -> per-character player rankings, a zip of CSVs downloaded by hand each month and read in place by `ds data char_ranking` (the newest zip in `~/Downloads`) into `../smash_db/parquet/char_ranking.parquet`. Steps: [char_ranking/README.md](char_ranking/README.md)

## start.gg's characters (`startgg/characters.py`)

start.gg's API names a game's pick by start.gg's own character id, so the start.gg code keeps
`STARTGG_CHARACTER_NAMES` (id -> start.gg's name, 87 picks) as a generated dict in `startgg/characters.py`.
`stored_characters()` turns it into `Character`s with our `char_group` and `char_icon`, so a player lookup
spends no request on the character list. `ds data startgg-char` rewrites the dict (one start.gg request);
Ultimate's roster is final, so only if start.gg renumbers. Stored data, not a cache: nothing refills it on its own.

It is code, not a SmashDb table: start.gg's ids are needed only to read its API. Nothing outside the start.gg
code sees them; callers get `char_group` (worked out from the name, plus `SITE_CHARACTER` for start.gg's
`Rosalina` and `Simon Belmont`). `tests/ds/data/test_startgg_api.py` checks every `CharGroup` is exactly one
start.gg character.
