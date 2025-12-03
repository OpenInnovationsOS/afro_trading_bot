import os
import pytest
from telegram.ext import Application

def test_bot_token_set():
    assert os.getenv("BOT_TOKEN"), "BOT_TOKEN not set"

def test_redis_connection():
    import redis
    r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    assert r.ping(), "Redis connection failed"

def test_tron_network():
    from src.tron_client import TronClient
    client = TronClient()
    assert client.get_block_height() > 0, "Failed to connect to TRON network"
