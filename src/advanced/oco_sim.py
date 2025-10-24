# src/advanced/oco_sim.py
"""
Simple simulated OCO: place a take-profit (limit) and stop-limit pair and, using polling, cancel the other when one fills.
This is a demo only — for production use websockets and robust state management.

Usage example (simulate):
python src/advanced/oco_sim.py BTCUSDT BUY 0.001 50000 48000 --simulate

Arguments:
SYMBOL SIDE QUANTITY TP_PRICE STOP_PRICE
"""
import argparse
import os
from dotenv import load_dotenv
import time
from src.common import BotConfig, make_client, logger, validate_symbol, validate_side, validate_quantity, log_api_call

POLL_INTERVAL = 2.0  # seconds

load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")
simulate_flag = os.getenv("SIMULATE", "0") == "1"


def place_oco_sim(client, cfg: BotConfig, symbol: str, side: str, quantity: float, tp_price: float, stop_price: float):
    """
    Simulation/demo: create two orders (take-profit limit and stop-limit).
    Poll order status and when one is FILLED, cancel the other.
    Note: true OCO semantics are more complex (stop trigger vs stop-limit).
    """
    # For simplicity we simulate placing two LIMIT orders with different prices
    tp_side = "SELL" if side.upper() == "BUY" else "BUY"
    stop_side = tp_side
    # Place orders
    # Using limit orders as placeholders; real stop-limit requires trigger logic
    from src.limit_orders import place_limit_order
    logger.info("Placing TP order at %s and STOP order at %s", tp_price, stop_price)
    tp_resp = place_limit_order(client, cfg, symbol, tp_side, quantity, tp_price)
    stop_resp = place_limit_order(client, cfg, symbol, stop_side, quantity, stop_price)
    logger.info("Placed OCO orders (simulated): tp=%s stop=%s", tp_resp, stop_resp)

    # Poll: in simulation mode we'll artificially "fill" one based on current time
    if cfg.simulate or client is None:
        # simulate fill of TP after a short time
        time.sleep(1)
        filled = tp_resp
        filled["status"] = "FILLED"
        logger.info("Simulated fill of TP order: %s", filled)
        # cancel the other
        stop_resp["status"] = "CANCELED"
        logger.info("Simulated cancel of STOP order: %s", stop_resp)
        return {"filled": filled, "canceled": stop_resp}

    # If real client: you'd implement order polling or websocket listen here.
    # For safety, we'll return the placed orders for the user to manage.
    return {"tp_order": tp_resp, "stop_order": stop_resp}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("symbol")
    parser.add_argument("side")
    parser.add_argument("quantity")
    parser.add_argument("tp_price", type=float)
    parser.add_argument("stop_price", type=float)
    parser.add_argument("--simulate", action="store_true")
    args = parser.parse_args()

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    cfg = BotConfig(api_key, api_secret, testnet=True, simulate=(args.simulate or os.getenv("SIMULATE","0")=="1"))

    if not validate_symbol(args.symbol) or not validate_side(args.side):
        logger.error("Invalid symbol or side")
        raise SystemExit(1)
    qty = validate_quantity(args.quantity)
    if qty is None:
        logger.error("Invalid quantity")
        raise SystemExit(1)

    try:
        client = make_client(cfg)
    except Exception as e:
        logger.warning("Client creation failed, switching to simulation: %s", e)
        cfg.simulate = True
        client = None

    result = place_oco_sim(client, cfg, args.symbol, args.side, qty, args.tp_price, args.stop_price)
    print(result)

if __name__ == "__main__":
    main()
