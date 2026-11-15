# Sources

Below details how gather raw data below:

_NOTE: this data is untransformed and normalized, just straight copy paste from source_

1. `raw_ko_kill_pct.csv` -> Mac Discord: copy paste from [link](https://docs.google.com/spreadsheets/d/1Fht5zTeF1p6C-79gOIPfZCorS_AIDgmgTezSbnThcAg/edit?gid=0#gid=0)
2. `framedata.py` -> scrapes [ultimateframedata.com](https://ultimateframedata.com) move frame data (`scrape_framedata(character)`, also exposed via `ds ssbu framedata <character>`)
3. `smashmate.py` -> downloads the character stock icons from [nasmashmate.com](https://nasmashmate.com/leaderboard) into `../char_icons/` (`scrape_char_icons(dest)`, exposed via `ds data char_icon`)
4. `supermajor.py` -> [supermajor.gg](https://www.supermajor.gg) player pages (character / stage usage). **Not working since Nov 2026**: the site's bot check blocks player pages. Its tag search (`search_players`) still works and is used to find start.gg player ids
5. `startgg/` -> [start.gg](https://www.start.gg)'s official GraphQL API (`client.py`, `queries.py`, `models.py`, `api.py`): a player's sets and games (characters, stages, results), tournaments, entrants, standings. Needs a token (`ds settings sync`). Check it live with `uv run scripts/startgg_probe.py`

What is computed from start.gg data (player usage, head-to-head, results) is not here but in `../startgg/`.
