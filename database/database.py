
import sqlite3
import hashlib
import os
from pathlib import Path


class Database:
    def __init__(self):
        Path("database").mkdir(exist_ok=True)
        self.path = Path("database/rps_evolution.db")

        with self.connect() as c:
            c.execute("""
                CREATE TABLE IF NOT EXISTS players(
                    username TEXT PRIMARY KEY,
                    salt TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    xp INTEGER DEFAULT 0,
                    highest_level INTEGER DEFAULT 0
                )
            """)

            c.execute("""
                CREATE TABLE IF NOT EXISTS matches(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    level INTEGER,
                    outcome TEXT,
                    player_score INTEGER,
                    robot_score INTEGER,
                    xp INTEGER,
                    played_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def connect(self):
        return sqlite3.connect(self.path)

    def digest(self, password, salt):
        salt_bytes = salt.encode("utf-8") if isinstance(salt, str) else salt

        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt_bytes,
            150000
        ).hex()

    def register(self, user, password):
        if len(user) < 3 or len(password) < 6:
            return False

        salt = os.urandom(16).hex()

        try:
            with self.connect() as c:
                c.execute(
                    """
                    INSERT INTO players(username, salt, password_hash)
                    VALUES (?, ?, ?)
                    """,
                    (user, salt, self.digest(password, salt))
                )
            return True

        except sqlite3.IntegrityError:
            return False

    def login(self, user, password):
        with self.connect() as c:
            row = c.execute(
                "SELECT salt, password_hash FROM players WHERE username=?",
                (user,)
            ).fetchone()

        return user if row and self.digest(password, row[0]) == row[1] else None

    def save_match(self, user, level, outcome, ps, rs, xp):
        with self.connect() as c:
            c.execute(
                """
                INSERT INTO matches(
                    username, level, outcome, player_score,
                    robot_score, xp
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user, level, outcome, ps, rs, xp)
            )

            c.execute(
                "UPDATE players SET xp=xp+? WHERE username=?",
                (xp, user)
            )

    def unlock_level(self, user, level):
        with self.connect() as c:
            c.execute(
                """
                UPDATE players
                SET highest_level = MAX(highest_level, ?)
                WHERE username=?
                """,
                (min(level + 1, 4), user)
            )

    def stats(self, user):
        with self.connect() as c:
            p = c.execute(
                "SELECT xp, highest_level FROM players WHERE username=?",
                (user,)
            ).fetchone()

            rows = c.execute(
                "SELECT outcome FROM matches WHERE username=? ORDER BY id",
                (user,)
            ).fetchall()

        if p is None:
            return None

        wins = sum(x[0] == "Victory" for x in rows)
        losses = sum(x[0] == "Defeat" for x in rows)
        draws = sum(x[0] == "Draw" for x in rows)

        streak = 0
        best = 0

        for (outcome,) in rows:
            streak = streak + 1 if outcome == "Victory" else 0
            best = max(best, streak)

        total = len(rows)

        return {
            "xp": p[0],
            "highest_level": p[1],
            "matches": total,
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "win_rate": wins / total * 100 if total else 0,
            "best_streak": best
        }

    def matches(self, user):
        with self.connect() as c:
            return c.execute(
                """
                SELECT level, outcome, player_score, robot_score, xp, played_at
                FROM matches
                WHERE username=?
                ORDER BY id DESC
                LIMIT 30
                """,
                (user,)
            ).fetchall()

    def change_username(self, old, new):
        if len(new) < 3:
            return False

        try:
            with self.connect() as c:
                c.execute(
                    "UPDATE players SET username=? WHERE username=?",
                    (new, old)
                )

                c.execute(
                    "UPDATE matches SET username=? WHERE username=?",
                    (new, old)
                )

            return True

        except sqlite3.IntegrityError:
            return False

    def change_password(self, user, old, new):
        if len(new) < 6:
            return False

        with self.connect() as c:
            row = c.execute(
                "SELECT salt, password_hash FROM players WHERE username=?",
                (user,)
            ).fetchone()

        if not row or self.digest(old, row[0]) != row[1]:
            return False

        salt = os.urandom(16).hex()

        with self.connect() as c:
            c.execute(
                """
                UPDATE players
                SET salt=?, password_hash=?
                WHERE username=?
                """,
                (salt, self.digest(new, salt), user)
            )

        return True
