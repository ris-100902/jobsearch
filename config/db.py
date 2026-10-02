import psycopg
import time

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
        self.last_insert_ts = time.time()

    def insert_jobs(self, jobs: list[dict]) -> list[dict]:
        "Insert jobs, returning only the new ones"
        now = time.time()
        self.last_insert_ts = now
        new = []
        for j in jobs:
            row = self.db.execute("SELECT id FROM jobs WHERE id = %s", (j["id"],)).fetchone()
            if row:
                self.db.execute("UPDATE jobs SET last_seen = %s, closed_at = NULL WHERE id = %s", (now, j["id"],))
            else:
                self.db.execute(
                    """INSERT INTO jobs(id, company, title, url, location, source,
                        posted_at, first_seen, last_seen, domain, description)
                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (j["id"], j["company"], j["title"], j["url"], j["location"],
                    j["source"], j["posted_at"], now, now, j["domain"], j["description"][:1500])
                )
                new.append(j)
        self.db.commit()
        return new
