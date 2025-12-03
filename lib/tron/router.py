from tronpy import Tron
from tronpy.contract import Contract
import json
import logging

logger = logging.getLogger(__name__)

# SunSwap V2 Router on Nile (verified 2025-12-03)
ROUTER_ADDRESS = "TGjYzgczKxFXTm36hF31F12hYzSg2JD7q8"
WTRX_ADDRESS = "TSdSj7h9U4fU7t3j5DJ6cE7Kk9r1K5U7Jw"

# Simplified ABI — only needed functions
ROUTER_ABI = [
    {
        "inputs": [
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"},
        ],
        "name": "swapExactTRXForTokens",
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"},
        ],
        "name": "swapExactTokensForTRX",
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "path", "type": "address[]"},
        ],
        "name": "getAmountsOut",
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function",
    },
]

class SunSwapRouter:
    def __init__(self, tron: Tron):
        self.tron = tron
        self.contract: Contract = tron.get_contract(ROUTER_ADDRESS)
        self.contract.abi = ROUTER_ABI

    async def get_amounts_out(self, amount_in_sun: int, path: list[str]) -> list[int]:
        """Return [amountIn, amountOut] in SUN."""
        try:
            result = await self.contract.functions.getAmountsOut(amount_in_sun, path)
            return result
        except Exception as e:
            logger.error(f"getAmountsOut failed: {e}")
            raise

    async def build_buy_tx(
        self,
        amount_trx: float,
        token_out: str,
        min_out_ratio: float = 0.95,  # 5% slippage
        deadline_sec: int = 1200,
    ) -> dict:
        """Build unsigned TRX→Token swap transaction."""
        amount_in_sun = int(amount_trx * 1_000_000)  # TRX → SUN
        path = [WTRX_ADDRESS, token_out]

        # Get expected output
        amounts = await self.get_amounts_out(amount_in_sun, path)
        amount_out_sun = amounts[-1]
        min_out_sun = int(amount_out_sun * min_out_ratio)

        # Build tx
        deadline = int(self.tron.get_now_block().timestamp) + deadline_sec
        tx = await self.contract.functions.swapExactTRXForTokens(
            min_out_sun, path, self.tron.default_address.hex, deadline
        ).with_owner(self.tron.default_address.hex).fee_limit(100_000_000).build()

        return {
            "tx": tx,
            "est_out_tokens": amount_out_sun,
            "min_out_tokens": min_out_sun,
            "path": path,
        }
