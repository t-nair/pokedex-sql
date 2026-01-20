# app.py
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="SQL Pokédex", layout="wide")

DB_PATH = "data/pokemon.db"

@st.cache_data(show_spinner=False)
def run_query(sql: str, params: tuple = ()):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn, params=params)

def ensure_db_exists():
    try:
        _ = run_query("SELECT name FROM sqlite_master LIMIT 1;")
    except Exception as e:
        st.error(
            f"Could not open DB at {DB_PATH}. "
            "Create it first (see backend guide)."
        )
        st.stop()

ensure_db_exists()

st.title("SQL Pokédex")
st.caption("A Pokédex-style dashboard powered by SQL (SQLite + Streamlit).")

# --- Sidebar controls ---
gens = run_query("SELECT DISTINCT generation FROM pokemon ORDER BY generation;")
if gens.empty:
    st.warning("Your DB has no Pokémon yet. Load data first.")
    st.stop()

gen_options = gens["generation"].tolist()
gen = st.sidebar.selectbox("Generation", gen_options, index=0)

search = st.sidebar.text_input("Search Pokémon name", placeholder="e.g., pikachu")

type_df = run_query("SELECT type_name FROM types ORDER BY type_name;")
type_options = ["(any)"] + type_df["type_name"].tolist()
type_filter = st.sidebar.selectbox("Type", type_options, index=0)

limit = st.sidebar.slider("Max rows", 10, 200, 30)

# --- Core filtered list (table) ---
filters = ["p.generation = ?"]
params = [gen]

if search.strip():
    filters.append("LOWER(p.name) LIKE ?")
    params.append(f"%{search.strip().lower()}%")

if type_filter != "(any)":
    filters.append("""
        EXISTS (
            SELECT 1
            FROM pokemon_types pt
            JOIN types t ON t.type_id = pt.type_id
            WHERE pt.pokemon_id = p.pokemon_id AND t.type_name = ?
        )
    """)
    params.append(type_filter)

where_clause = " AND ".join(filters)

sql_list = f"""
SELECT
  p.pokemon_id,
  p.name,
  p.height,
  p.weight,
  p.sprite_url,
  s.hp, s.atk, s.def, s.spa, s.spd, s.spe,
  (s.hp + s.atk + s.def + s.spa + s.spd + s.spe) AS total_stats
FROM pokemon p
JOIN stats s ON s.pokemon_id = p.pokemon_id
WHERE {where_clause}
ORDER BY total_stats DESC
LIMIT ?
"""
params_list = tuple(params + [limit])
df = run_query(sql_list, params_list)

# --- Top row: Highlights ---
colA, colB, colC = st.columns(3)

biggest = run_query(
    """
    SELECT p.name, p.height, p.weight, p.sprite_url
    FROM pokemon p
    WHERE p.generation = ?
    ORDER BY p.height DESC, p.weight DESC
    LIMIT 1
    """,
    (gen,),
)

heaviest = run_query(
    """
    SELECT p.name, p.weight, p.height, p.sprite_url
    FROM pokemon p
    WHERE p.generation = ?
    ORDER BY p.weight DESC, p.height DESC
    LIMIT 1
    """,
    (gen,),
)

fastest = run_query(
    """
    SELECT p.name, s.spe AS speed, p.sprite_url
    FROM pokemon p
    JOIN stats s ON s.pokemon_id = p.pokemon_id
    WHERE p.generation = ?
    ORDER BY s.spe DESC
    LIMIT 1
    """,
    (gen,),
)

def highlight_card(container, title, row):
    container.subheader(title)
    if row.empty:
        container.info("No data yet.")
        return
    r = row.iloc[0].to_dict()
    left, right = container.columns([1, 2])
    if r.get("sprite_url"):
        left.image(r["sprite_url"], width=120)
    right.write(f"**{r.get('name','')}**")
    # Show remaining fields
    for k, v in r.items():
        if k in ("name", "sprite_url"):
            continue
        right.write(f"- {k}: {v}")

highlight_card(colA, "Biggest (height)", biggest)
highlight_card(colB, "Heaviest (weight)", heaviest)
highlight_card(colC, "Fastest", fastest)

st.divider()

# --- Type distribution ---
st.subheader("Type distribution (selected generation)")
type_dist = run_query(
    """
    SELECT t.type_name, COUNT(*) AS count
    FROM pokemon p
    JOIN pokemon_types pt ON pt.pokemon_id = p.pokemon_id
    JOIN types t ON t.type_id = pt.type_id
    WHERE p.generation = ?
    GROUP BY t.type_name
    ORDER BY count DESC, t.type_name ASC
    """,
    (gen,),
)

left, right = st.columns([1, 2])
left.dataframe(type_dist, use_container_width=True, hide_index=True)

# Simple bar chart without specifying colors
if not type_dist.empty:
    chart_df = type_dist.set_index("type_name")
    right.bar_chart(chart_df)

st.divider()

# --- Pokédex list with images ---
st.subheader("Pokédex list (filtered)")
if df.empty:
    st.info("No Pokémon match your filters.")
else:
    # Show as cards
    for _, row in df.iterrows():
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 2, 2])
            if row["sprite_url"]:
                c1.image(row["sprite_url"], width=96)
            c2.markdown(f"### {row['name'].title()}  \nID: `{row['pokemon_id']}`")
            c2.write(f"Gen {gen} | Height: {row['height']} | Weight: {row['weight']}")
            c2.write(f"Type filter: {type_filter}")
            c3.write("**Stats**")
            c3.write(
                f"HP {row['hp']} | ATK {row['atk']} | DEF {row['def']} | "
                f"SpA {row['spa']} | SpD {row['spd']} | SPE {row['spe']}"
            )
            c3.write(f"**Total**: {row['total_stats']}")

