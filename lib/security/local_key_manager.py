import os
import logging
from tronpy import Tron
from tronpy.keys import PrivateKey
from .key_manager import KeyManager

logger = logging.getLogger(__name__)

class LocalKeyManager(KeyManager):
    """Dev-only key manager. NEVER use in production."""

    def __init__(self, tron: Tron):
        self.tron = tron
        key_hex = os.getenv("LOCAL_PRIVATE_KEY")
        if not key_hex:
            # Generate ephemeral testnet key
            self.private_key = PrivateKey.random()
            key_hex = self.private_key.hex()
            os.environ["LOCAL_PRIVATE_KEY"] = key_hex
            addr = self.private_key.public_key.to_base58check_address()
            logger.warning(
                "⚠️  GENERATED EPHEMERAL TESTNET PRIVATE KEY (save if needed):\n"
                f"Address: {addr}\n"
                f"Private Key (hex): {key_hex}\n"
                "🛑 DO NOT USE IN PRODUCTION. DELETE AFTER TESTNET TESTING."
            )
        else:
            self.private_key = PrivateKey(bytes.fromhex(key_hex))

    async def get_address(self) -> str:
        return self.private_key.public_key.to_base58check_address()

    async def sign_transaction(self, raw_tx: dict) -> str:
        tx = self.tron.trx._build_transaction(raw_tx)
        tx.sign(self.private_key)
        return tx.txid, tx

    async def get_nonce(self) -> int:
        addr = await self.get_address()
        return await self.tron.get_account(addr).get("balance", 0)  # placeholder
