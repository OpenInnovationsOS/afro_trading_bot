import pytest
from src.wallet import Wallet

def test_wallet_creation():
    w = Wallet("your_private_key_here")
    assert w.address.startswith("T")
