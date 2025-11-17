import logging
import sqlite3
import asyncio
import config

from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Dispatcher, Bot, BaseMiddleware
from typing import Any, Callable, Dict, Awaitable
from handlers import start, chat, casino, ref
from aiogram.types import TelegramObject

class BanCheckMiddleware_call(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]):
        user = data["event_from_user"]
        user_id = user.id

        if user_id:
            cursor.execute("SELECT ban FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if result and result[0] == 1:
                await event.answer("Вы были заблокированы.", show_alert=True)
                return
            else:
                await handler(event, data)
        else:
            await handler(event, data)

class BanCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]):
        user = data["event_from_user"]
        user_id = user.id

        if user_id:
            cursor.execute("SELECT ban FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if result and result[0] == 1:
                await event.answer("<b>Вы были заблокированы.</b>")
                return
            else:
                await handler(event, data)
        else:
            await handler(event, data)

conn = sqlite3.connect("db.db")
cursor = conn.cursor()

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(start.router, chat.router, casino.router, ref.router)

    dp.callback_query.outer_middleware(BanCheckMiddleware_call())
    dp.message.outer_middleware(BanCheckMiddleware())

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == '__main__':
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INT,
        first_name TEXT,
        balance REAL DEFAULT 0,
        total_got REAL DEFAULT 0,
        level INT DEFAULT 1,
        ref INT,
        mod INT DEFAULT 0,
        ban INT DEFAULT 0,
        username TEXT,
        correct_emoji TEXT,
        poll_msg TEXT,
        welcome_msg TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        win INT DEFAULT 0,
        lose INT DEFAULT 0,
        draw INT DEFAULT 0,
        amount REAL DEFAULT 0,
        win_amount REAL DEFAULT 0,
        user_id INT
    );""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS podkrut(
        podkrut_status INT DEFAULT 0,
        prokrut INT DEFAULT 2
    );""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        top1 TEXT DEFAULT 'Пустое место',
        top1_summa REAL DEFAULT 0.0,
        top2 TEXT DEFAULT 'Пустое место',
        top2_summa REAL DEFAULT 0.0,
        top3 TEXT DEFAULT 'Пустое место',
        top3_summa REAL DEFAULT 0.0,
        end_date DATETIME,
        win_amount REAL,
        msg_id INT,
        end INT DEFAULT 0
    );""")
    conn.commit()

    exist = cursor.execute("SELECT * FROM podkrut").fetchone()
    if not exist:
        cursor.execute("INSERT INTO podkrut(podkrut_status) VALUES(0)")
        conn.commit()

    asyncio.run(main())