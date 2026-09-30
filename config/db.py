import psycopg
from psycopg import Error

CREATE_TABLE = '''
    CREATE TABLE IF NOT EXISTS jobs (
    id          TEXT PRIMARY KEY,
    company     TEXT NOT NULL,
    title       TEXT NOT NULL,
    url         TEXT,
    location    TEXT,
    source      TEXT,
    posted_at   REAL,
    first_seen  REAL NOT NULL,
    last_seen   REAL NOT NULL,
    closed_at   REAL,
    score       INTEGER,
    reason      TEXT,
    notified    BOOLEAN,
    domain      TEXT,
    breakdown   TEXT,
    alerted     BOOLEAN,
    description TEXT
);
'''

class Db:
    def __init__(self):
        self.db = psycopg.connect(user="postgres",
                                password="TROUBADOR!",
                                host="127.0.0.1",
                                port="5432",
                                dbname="jobsearch")
        cursor = self.db.cursor()
        cursor.execute(CREATE_TABLE)
        self.db.commit()
        cursor.close()
        self.db.close()