PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS pokemon (
  pokemon_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  generation INTEGER NOT NULL,
  height INTEGER,
  weight INTEGER,
  sprite_url TEXT
);

CREATE TABLE IF NOT EXISTS stats (
  pokemon_id INTEGER PRIMARY KEY,
  hp INTEGER, atk INTEGER, def INTEGER, spa INTEGER, spd INTEGER, spe INTEGER,
  FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS types (
  type_id INTEGER PRIMARY KEY AUTOINCREMENT,
  type_name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS pokemon_types (
  pokemon_id INTEGER NOT NULL,
  type_id INTEGER NOT NULL,
  PRIMARY KEY (pokemon_id, type_id),
  FOREIGN KEY (pokemon_id) REFERENCES pokemon(pokemon_id) ON DELETE CASCADE,
  FOREIGN KEY (type_id) REFERENCES types(type_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_pokemon_generation ON pokemon(generation);
CREATE INDEX IF NOT EXISTS idx_pokemon_name ON pokemon(name);
