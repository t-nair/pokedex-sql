# load_data.py
import sqlite3
import requests
from typing import Dict, List

DB_PATH = "data/pokemon.db"

# ID ranges (simple approach). Adjust if you want only certain gens.
GEN_ID_RANGES = {
    1: (1, 151),
    2: (152, 251),
    3: (252, 386),
    4: (387, 493),
    5: (494, 649),
    6: (650, 721),
    7: (722, 809),
    8: (810, 905),
    9: (906, 1025),  # may change over time
}

def get_json(url: str) -> Dict:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def upsert_type(conn, type_name: str) -> int:
    conn.execute("INSERT OR IGNORE INTO types(type_name) VALUES (?)", (type_name,))
    return conn.execute("SELECT type_id FROM types WHERE type_name = ?", (type_name,)).fetchone()[0]

def load_generation(gen: int):
    start, end = GEN_ID_RANGES[gen]
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        for pid in range(start, end + 1):
            data = get_json(f"https://pokeapi.co/api/v2/pokemon/{pid}")
            name = data["name"]
            height = data.get("height")
            weight = data.get("weight")
            sprite = (data.get("sprites") or {}).get("front_default")

            # Stats mapping
            stat_map = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
            hp = stat_map.get("hp")
            atk = stat_map.get("attack")
            dfn = stat_map.get("defense")
            spa = stat_map.get("special-attack")
            spd = stat_map.get("special-defense")
            spe = stat_map.get("speed")

            conn.execute(
                """
                INSERT OR REPLACE INTO pokemon(pokemon_id, name, generation, height, weight, sprite_url)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (pid, name, gen, height, weight, sprite),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO stats(pokemon_id, hp, atk, def, spa, spd, spe)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (pid, hp, atk, dfn, spa, spd, spe),
            )

            # Types (many-to-many)
            conn.execute("DELETE FROM pokemon_types WHERE pokemon_id = ?", (pid,))
            for t in data["types"]:
                type_name = t["type"]["name"]
                type_id = upsert_type(conn, type_name)
                conn.execute(
                    "INSERT OR IGNORE INTO pokemon_types(pokemon_id, type_id) VALUES (?, ?)",
                    (pid, type_id),
                )

        conn.commit()

if __name__ == "__main__":
    # Start small so you finish today:
    # load gen 1 first, then 2, then 3 if you have time.
    for gen in sorted(GEN_ID_RANGES.keys()):
        print(f"Loading gen {gen}...")
        load_generation(gen)
    print("Done.")
