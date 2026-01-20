# pokedex-sql
A SQL-powered Pokedex! This dashboard allows users to explore Pokémon data by generation and surface meaningful insights using SQL queries. All analytics and views are powered directly from a local SQLite database.

Key features include:
* Generation-based filtering
* Biggest, heaviest, and fastest Pokémon per generation
* Type distribution analysis
* Stat aggregation and ranking
* Pokédex-style list with sprites

## details
Built with SQL (joins, aggregations, indexing, filtering), SQLite (relational database), Python (data ingestion and backend logic), Streamlit (frontend dashboard), and PokeAPI (data source for Pokémon stats and sprites). 

The project uses a normalized relational schema:
* pokemon: core Pokémon attributes and generation
* stats: base stats (HP, Attack, Defense, etc.)
* types: Pokémon types
* pokemon_types: many-to-many mapping between Pokémon and types

## directory structure
```
pokedex-sql/
├── README.md
├── data/
│   └── pokemon.db
├── schema.sql
├── load_data.py
├── queries.sql
├── app.py         
└── requirements.txt

```
