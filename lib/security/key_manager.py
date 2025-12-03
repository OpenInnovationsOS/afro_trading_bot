from abc import ABC, abstractmethod
from typing import Tuple

class KeyManager(ABC):
    """Abstract interface for signing. Swappable for KMS/HSM."""

    @abstractmethod
    async def get_address(self) -> str:
        """Return public address (base58)."""
        pass

    @abstractmethod
    async def sign_transaction(self, raw_tx: dict) -> str:
        """Sign raw transaction and return signed hex string."""
        pass

    @abstractmethod
    async def get_nonce(self) -> int:
        """Get current account nonce (for collision avoidance)."""
        pass
