import os
from tronpy import Tron
from tronpy.providers import HTTPProvider

def get_tron_client() -> Tron:
    network = os.getenv("TRON_NETWORK", "nile")
    if network == "nile":
        provider = HTTPProvider(
            api_key=os.getenv("TRON_API_KEY"),  # optional
            endpoint_uri=os.getenv("TRON_FULLNODE", "https://api.nileex.io"),
        )
        return Tron(provider=provider, network="nile")
    elif network == "mainnet":
        return Tron(network="mainnet")
    else:
        raise ValueError(f"Unknown network: {network}")
