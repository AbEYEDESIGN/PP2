import psycopg2

DB_CONFIG = {
    "dbname": "snake_db",
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": "5432"
}

def connect():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """создаём таблицы если их нет"""
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        create table if not exists players (
            id       serial primary key,
            username varchar(50) unique not null
        )
    """)
    cur.execute("""
        create table if not exists game_sessions (
            id            serial primary key,
            player_id     integer references players(id),
            score         integer   not null,
            level_reached integer   not null,
            played_at     timestamp default now()
        )
    """)
    conn.commit()
    conn.close()


def get_or_create_player(username):
    """возвращает id игрока, создаёт запись если нет"""
    conn = connect()
    cur = conn.cursor()
    cur.execute("select id from players where username = %s", (username,))
    row = cur.fetchone()
    if row:
        pid = row[0]
    else:
        cur.execute("insert into players (username) values (%s) returning id", (username,))
        pid = cur.fetchone()[0]
        conn.commit()
    conn.close()
    return pid


def save_session(player_id, score, level):
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        insert into game_sessions (player_id, score, level_reached)
        values (%s, %s, %s)
    """, (player_id, score, level))
    conn.commit()
    conn.close()


def get_top10():
    """топ 10 результатов всех игроков"""
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        select p.username, gs.score, gs.level_reached,
               to_char(gs.played_at, 'DD.MM.YY') as dt
        from game_sessions gs
        join players p on gs.player_id = p.id
        order by gs.score desc
        limit 10
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_personal_best(player_id):
    """лучший результат конкретного игрока"""
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        select max(score) from game_sessions where player_id = %s
    """, (player_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row and row[0] else 0
