# src/market_orders.py
"""
Usage (CLI):
python src/market_orders.py SYMBOL SIDE QUANTITY [--simulate]

Examples:
python src/market_orders.py BTCUSDT BUY 0.001
python src/market_orders.py ETHUSDT SELL 0.05 --simulate
"""
import argparse
import os
from dotenv import load_dotenv
from src.common import BotConfig, make_client, logger, validate_symbol, validate_side, validate_quantity, log_api_call

load_dotenv()



def place_market_order(client, cfg: BotConfig, symbol: str, side: str, quantity: float, reduce_only: bool=False):
    payload = {
        "symbol": symbol,
        "side": side.upper(),
        "type": "MARKET",
        "quantity": quantity,
        "reduceOnly": reduce_only
    }
    try:
        if cfg.simulate or client is None:
            # simulated response
            resp = {
                "orderId": 123456,
                "symbol": symbol,
                "side": side.upper(),
                "status": "FILLED",
                "executedQty": quantity,
                "avgPrice": "market_price_simulated"
            }
            log_api_call("futures_create_order (SIMULATED)", payload, resp)
            return resp
        else:
            # For futures, python-binance client uses client.futures_create_order
            resp = client.futures_create_order(**payload)
            log_api_call("futures_create_order", payload, resp)
            return resp
    except Exception as e:
        log_api_call("futures_create_order", payload, None, e)
        raise

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("symbol", help="Trading pair e.g., BTCUSDT")
    parser.add_argument("side", help="BUY or SELL")
    parser.add_argument("quantity", help="Quantity (in base asset units)")
    parser.add_argument("--simulate", action="store_true", help="Run in simulation mode (no API calls)")
    args = parser.parse_args()

    # load API keys from env
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    # respect CLI simulate flag
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

    client = None
    try:
        client = make_client(cfg)
    except Exception as e:
        logger.warning("Client creation failed, switching to simulation: %s", e)
        cfg.simulate = True  # fallback to simulate
        client = None

    resp = place_market_order(client, cfg, args.symbol, args.side, qty)
    logger.info("Order response: %s", resp)
    print(resp)

if __name__ == "__main__":
    main()
