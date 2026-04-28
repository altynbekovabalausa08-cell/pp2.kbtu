import psycopg2
from psycopg2 import sql

# Change these to match your PostgreSQL setup
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "snake_game",
    "user": "postgres",
    "password": "1234",
}


def get_conn():
    """Open and return a DB connection."""
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """Create tables if they don't exist yet."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id       SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS game_sessions (
            id            SERIAL PRIMARY KEY,
            player_id     INTEGER REFERENCES players(id),
            score         INTEGER   NOT NULL,
            level_reached INTEGER   NOT NULL,
            played_at     TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def get_or_create_player(username):
    """Return player id; insert new row if username is new."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    row = cur.fetchone()
    if row:
        player_id = row[0]
    else:
        cur.execute("INSERT INTO players (username) VALUES (%s) RETURNING id", (username,))
        player_id = cur.fetchone()[0]
        conn.commit()
    cur.close()
    conn.close()
    return player_id


def save_session(player_id, score, level):
    """Save one game result to game_sessions."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
        (player_id, score, level)
    )
    conn.commit()
    cur.close()
    conn.close()


def get_personal_best(player_id):
    """Return the highest score for this player (0 if none)."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT COALESCE(MAX(score), 0) FROM game_sessions WHERE player_id = %s",
        (player_id,)
    )
    best = cur.fetchone()[0]
    cur.close()
    conn.close()
    return best


def get_top10():
    """Return top 10 rows: (rank, username, score, level, date)."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.username, gs.score, gs.level_reached,
               TO_CHAR(gs.played_at, 'YYYY-MM-DD')
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        ORDER BY gs.score DESC
        LIMIT 10;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # add rank number
    return [(i + 1,) + row for i, row in enumerate(rows)]