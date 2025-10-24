# src/advanced/twap.py
"""
TWAP (simple): Split a target quantity into n chunks and send market orders spaced across duration_seconds.

Usage:
python src/advanced/twap.py SYMBOL SIDE TOTAL_QTY NUM_CHUNKS DURATION_SECONDS [--simulate]

Example:
python src/advanced/twap.py BTCUSDT BUY 0.05 5 60 --simulate
"""
import argparse
import os
from dotenv import load_dotenv
import time
from src.common import BotConfig, make_client, logger, validate_symbol, validate_side, validate_quantity


load_dotenv()



def run_twap(client, cfg: BotConfig, symbol: str, side: str, total_qty: float, chunks: int, duration_seconds: int):
    if chunks <= 0:
        raise ValueError("chunks must be positive")
    chunk_qty = round(total_qty / chunks, 8)  # rounding to avoid very long floats
    interval = duration_seconds / chunks if duration_seconds > 0 else 0
    logger.info("Starting TWAP: %s %s total_qty=%s chunks=%d interval=%.2f", symbol, side, total_qty, chunks, interval)
    results = []
    for i in range(chunks):
        logger.info("TWAP chunk %d/%d: placing market order qty=%s", i+1, chunks, chunk_qty)
        from src.market_orders import place_market_order  # local import to avoid circular at top-level
        resp = place_market_order(client, cfg, symbol, side, chunk_qty)
        results.append(resp)
        if i < chunks - 1:
            time.sleep(interval)
    logger.info("TWAP completed: placed %d orders", len(results))
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("symbol")
    parser.add_argument("side")
    parser.add_argument("total_qty")
    parser.add_argument("chunks", type=int)
    parser.add_argument("duration_seconds", type=int)
    parser.add_argument("--simulate", action="store_true")
    args = parser.parse_args()

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    cfg = BotConfig(api_key, api_secret, testnet=True, simulate=(args.simulate or os.getenv("SIMULATE","0")=="1"))

    if not validate_symbol(args.symbol) or not validate_side(args.side):
        logger.error("Invalid symbol or side")
        raise SystemExit(1)
    qty = validate_quantity(args.total_qty)
    if qty is None:
        logger.error("Invalid total quantity")
        raise SystemExit(1)

    try:
        client = make_client(cfg)
    except Exception as e:
        logger.warning("Client creation failed, switching to simulation: %s", e)
        cfg.simulate = True
        client = None

    results = run_twap(client, cfg, args.symbol, args.side, qty, args.chunks, args.duration_seconds)
    print(results)

if __name__ == "__main__":
    main()
