# src/common.py
import os
from dotenv import load_dotenv
import logging
import time
from typing import Optional, Dict, Any

load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
simulate_flag = os.getenv("SIMULATE", "0") == "1"

try:
    # python-binance library
    from binance.client import Client as BinanceClient
except Exception:
    BinanceClient = None  # allow mock mode if library not installed

LOG_FILE = os.getenv("BOT_LOG_FILE", "bot.log")

# Configure logger
logger = logging.getLogger("binance_bot")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
# File handler
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)
# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

class BotConfig:
    def __init__(self, api_key: Optional[str], api_secret: Optional[str], testnet: bool = True, simulate: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.simulate = simulate

def make_client(cfg: BotConfig):
    """
    Return a Binance client configured for USDT-M Futures.
    If cfg.simulate is True, returns None and code will simulate responses.
    """
    if cfg.simulate:
        logger.info("Simulated client requested - running in simulation mode (no live API calls).")
        return None

    if BinanceClient is None:
        raise RuntimeError("python-binance library not available. Install with `pip install python-binance` or set SIMULATE=1 to run in simulation mode.")

    client = BinanceClient(cfg.api_key, cfg.api_secret, testnet=cfg.testnet)
    server_time = client.futures_time()
    client.timestamp_offset = server_time['serverTime'] - int(time.time() * 1000)

    # For futures on python-binance, testnet usage requires specifying base url for futures: the python-binance client has set_api_key/secret; ensure environment var or pass url if needed.
    # If using python-binance >=1.0, you may need to set client.API_URL or pass keyword; check your installed lib docs.
    return client

# Basic validators
def validate_symbol(symbol: str) -> bool:
    # Very basic validation: non-empty and all uppercase letters/numbers
    if not symbol or not isinstance(symbol, str):
        return False
    # Real validation should call exchange info. Keep simple here.
    return symbol.isalnum() and symbol.upper() == symbol

def validate_side(side: str) -> bool:
    return side.upper() in ("BUY", "SELL")

def validate_quantity(qty_str: str) -> Optional[float]:
    try:
        q = float(qty_str)
        if q <= 0:
            return None
        return q
    except Exception:
        return None

def log_api_call(action: str, payload: Dict[str, Any], response: Any=None, error: Optional[Exception]=None):
    if error:
        logger.exception("API action=%s payload=%s error=%s", action, payload, error)
    else:
        logger.info("API action=%s payload=%s response=%s", action, payload, response if response is not None else "NO RESPONSE")
