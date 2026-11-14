# Mission audit

Static check of which mission trees every starting nation can see at game start (304 BC),
assuming all DLC and a human player. It reads the mod's `setup/main/00_default.txt`, the map
(adjacency from `provinces.png`), pop cultures, and every mission's `potential`, evaluating them
as True / False / unknown.

    python3 tools/mission_audit/audit.py <Invictus dir> <this repo>
    python3 tools/mission_audit/summary.py [TAG ...]

`summary.py` prints how many nations have zero missions and the missions available to the tags you list.
Needs `numpy` and `Pillow`. The first run builds `adj_cache.json` (delete it if the map changes).
It approximates the game's script engine, so treat "unknown" results and edge cases with care.
