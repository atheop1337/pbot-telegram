import os
import aiosqlite
import logging

from typing_extensions import Optional, Dict, Union

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.database = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", ".database", "pbot.db"))

    async def create_tables(self) -> None:
        """Creating tables"""
        async with aiosqlite.connect(self.database) as db:
            async with db.cursor() as cursor:
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER UNIQUE NOT NULL,
                        username TEXT,
                        language TEXT NOT NULL DEFAULT 'en',
                        registration_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        balance INTEGER NOT NULL DEFAULT 0,
                        goods_owned TEXT NOT NULL DEFAULT '[]',
                        is_admin INTEGER NOT NULL DEFAULT 0
                    );
                """)
            await db.commit()
            logger.info("Tables created successfully")

    async def create_user(self, user_id: int, username: str, language: str) -> Optional[Union[bool, int]]:
        async with aiosqlite.connect(self.database) as db:
            async with db.cursor() as cursor:
                try:
                    await cursor.execute(
                        "INSERT INTO users (user_id, username, language) VALUES (?, ?, ?)",
                        (user_id, username, language)
                    )
                    await db.commit()
                    logger.info(f"User created: user_id={user_id}, username={username}, language={language}")
                    return True
                except aiosqlite.IntegrityError:
                    await db.rollback()
                    logger.info(f"User already exists: user_id={user_id}")
                    return 403
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Error creating user: user_id={user_id}, error={e}")
                    return None

    async def fetch_info(self, user_id: int) -> Union[Dict[str, any], bool]:
        async with aiosqlite.connect(self.database) as db:
            async with db.cursor() as cursor:
                try:
                    await cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                    rows = await cursor.fetchone()
                    if rows is None:
                        logger.info(f"User not found: user_id={user_id}")
                        return None
                    logger.info(f"Fetched user info: user_id={user_id}")
                    return {
                        "id": rows[0],
                        "user_id": rows[1],
                        "username": rows[2],
                        "language": rows[3],
                        "registration_date": rows[4],
                        "balance": rows[5],
                        "goods_owned": rows[6],
                        "is_admin": rows[7]
                    }
                except aiosqlite.Error as e:
                    logger.error(f"Error fetching user info: user_id={user_id}, error={e}")
                    return False

    async def update_user(self, user_id: int, identity: str, value: Union[str, int, bool]) -> Union[bool, int]:
        async with aiosqlite.connect(self.database) as db:
            async with db.cursor() as cursor:
                try:
                    await cursor.execute(f"UPDATE users SET {identity} = ? WHERE user_id = ?", (value, user_id))
                    await db.commit()
                    logger.info(f"User updated: user_id={user_id}, field={identity}, new_value={value}")

                    if identity == "language":
                        logger.info(f"Language selection: user_id={user_id}, new_language={value}")

                    return True
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Error updating user: user_id={user_id}, field={identity}, error={e}")
                    return False
