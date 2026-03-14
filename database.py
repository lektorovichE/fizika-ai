import aiosqlite
from datetime import datetime

DB_PATH = "fizai.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                age INTEGER,
                weight REAL,
                height REAL,
                goal TEXT,
                activity_level TEXT,
                subscription_status TEXT DEFAULT 'free',
                subscription_end_date TEXT,
                free_analyses_used INTEGER DEFAULT 0,
                onboarding_done INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                created_at TEXT,
                result_text TEXT,
                body_fat_range TEXT,
                body_type TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                payment_id TEXT,
                amount REAL,
                status TEXT,
                created_at TEXT
            )
        """)
        await db.commit()

async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

async def create_user(user_id: int, username: str, first_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().isoformat()
        await db.execute(
            """INSERT OR IGNORE INTO users 
               (user_id, username, first_name, created_at, updated_at) 
               VALUES (?,?,?,?,?)""",
            (user_id, username, first_name, now, now)
        )
        await db.commit()

async def update_user(user_id: int, **kwargs):
    if not kwargs:
        return
    kwargs["updated_at"] = datetime.now().isoformat()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {sets} WHERE user_id = ?", vals)
        await db.commit()

async def save_analysis(user_id: int, result_text: str, body_fat_range: str, body_type: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO analyses (user_id, created_at, result_text, body_fat_range, body_type) VALUES (?,?,?,?,?)",
            (user_id, datetime.now().isoformat(), result_text, body_fat_range, body_type)
        )
        await db.execute(
            "UPDATE users SET free_analyses_used = free_analyses_used + 1, updated_at = ? WHERE user_id = ?",
            (datetime.now().isoformat(), user_id)
        )
        await db.commit()

async def get_analyses(user_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM analyses WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
            (user_id,)
        ) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

async def delete_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM analyses WHERE user_id = ?", (user_id,))
        await db.execute("DELETE FROM payments WHERE user_id = ?", (user_id,))
        await db.commit()

async def get_stats() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            total_users = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM users WHERE subscription_status = 'active'") as cur:
            active_subs = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM analyses") as cur:
            total_analyses = (await cur.fetchone())[0]
    return {
        "total_users": total_users,
        "active_subs": active_subs,
        "total_analyses": total_analyses
    }

async def activate_subscription(user_id: int, payment_id: str):
    from datetime import timedelta
    end_date = (datetime.now() + timedelta(days=30)).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET subscription_status='active', subscription_end_date=?, updated_at=? WHERE user_id=?",
            (end_date, datetime.now().isoformat(), user_id)
        )
        await db.execute(
            "INSERT INTO payments (user_id, payment_id, amount, status, created_at) VALUES (?,?,599,'succeeded',?)",
            (user_id, payment_id, datetime.now().isoformat())
        )
        await db.commit()
