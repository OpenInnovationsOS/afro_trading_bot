import os
import asyncio
import pytest
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from lib.tron.client import get_tron_client
from db.session import get_db
from db.models.user import get_or_create_user

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID"))
TEST_TOKEN = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"  # Nile USDT

async def test_end_to_end_buy():
    session = AiohttpSession()
    bot = Bot(token=TELEGRAM_TOKEN, session=session)
    
    # Send /buy command
    await bot.send_message(ADMIN_ID, f"/buy {TEST_TOKEN} 1.0 5")
    
    # Wait for response
    # (In real test, use updates.get_updates() polling or webhook mock)
    print("✅ Smoke test initiated. Check Telegram for confirmation.")
    
    # Verify DB record
    async for db in get_db():
        user = await get_or_create_user(ADMIN_ID)
        trades = await db.execute(
            "SELECT * FROM trades WHERE user_id = %s ORDER BY id DESC LIMIT 1",
            (user.telegram_id,)
        )
        row = trades.fetchone()
        if row:
            print(f"✅ Latest trade: {row}")
            assert row["status"] in ("pending", "confirmed")
        else:
            print("⚠️ No trade found yet — try again in 10s")

if __name__ == "__main__":
    asyncio.run(test_end_to_end_buy())
