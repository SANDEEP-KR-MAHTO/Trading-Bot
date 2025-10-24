# src/limit_orders.py
"""
Usage:
python src/limit_orders.py SYMBOL SIDE QUANTITY PRICE [--timeInForce GTC] [--simulate]

Example:
python src/limit_orders.py BTCUSDT BUY 0.001 45000 --timeInForce GTC --simulate
"""
import argparse
import os
from dotenv import load_dotenv
from src.common import BotConfig, make_client, logger, validate_symbol, validate_side, validate_quantity, log_api_call

VALID_TIMEINFORCE = {"GTC", "IOC", "FOK"}

load_dotenv()



def place_limit_order(client, cfg: BotConfig, symbol: str, side: str, quantity: float, price: float, timeInForce: str="GTC", reduce_only: bool=False):
    payload = {
        "symbol": symbol,
        "side": side.upper(),
        "type": "LIMIT",
        "quantity": quantity,
        "price": str(price),
        "timeInForce": timeInForce,
        "reduceOnly": reduce_only
    }
    try:
        if cfg.simulate or client is None:
            resp = {
                "orderId": 654321,
                "symbol": symbol,
                "side": side.upper(),
                "status": "NEW",
                "price": str(price),
                "origQty": quantity
            }
            log_api_call("futures_create_order (SIMULATED)", payload, resp)
            return resp
        else:
            resp = client.futures_create_order(**payload)
            log_api_call("futures_create_order", payload, resp)
            return resp
    except Exception as e:
        log_api_call("futures_create_order", payload, None, e)
        raise

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("symbol")
    parser.add_argument("side")
    parser.add_argument("quantity")
    parser.add_argument("price")
    parser.add_argument("--timeInForce", default="GTC", help="GTC/IOC/FOK")
    parser.add_argument("--simulate", action="store_true")
    args = parser.parse_args()

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    simulate_flag = args.simulate or os.getenv("SIMULATE", "0") == "1"
    cfg = BotConfig(api_key, api_secret, testnet=True, simulate=simulate_flag)

    if not validate_symbol(args.symbol):
        logger.error("Invalid symbol: %s", args.symbol)
        raise SystemExit(1)
    if not validate_side(args.side):
        logger.error("Invalid side: %s", args.side)
        raise SystemExit(1)
    qty = validate_quantity(args.quantity)
    if qty is None:
        logger.error("Invalid quantity: %s", args.quantity)
        raise SystemExit(1)
    try:
        price = float(args.price)
        if price <= 0:
            raise ValueError()
    except Exception:
        logger.error("Invalid price: %s", args.price)
        raise SystemExit(1)
    tif = args.timeInForce.upper()
    if tif not in VALID_TIMEINFORCE:
        logger.error("Invalid timeInForce: %s", tif)
        raise SystemExit(1)

    client = None
    try:
        client = make_client(cfg)
    except Exception as e:
        logger.warning("Client creation failed, switching to simulation: %s", e)
        cfg.simulate = True
        client = None

    resp = place_limit_order(client, cfg, args.symbol, args.side, qty, price, tif)
    logger.info("Limit order response: %s", resp)
    print(resp)

if __name__ == "__main__":
    main()
