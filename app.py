import streamlit as st
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

# Detect Streamlit Cloud environment
is_cloud = os.getenv("STREAMLIT_RUNTIME", "") != ""

# Read API keys
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# Force simulation mode on Streamlit Cloud
simulate_flag = True if is_cloud else (os.getenv("SIMULATE", "0") == "1")

# Lazy import your project modules
from src.common import BotConfig, make_client, logger, validate_symbol, validate_side, validate_quantity
from src.market_orders import place_market_order
from src.limit_orders import place_limit_order

# Build config
cfg = BotConfig(api_key, api_secret, testnet=True, simulate=simulate_flag)

# ✅ Only create Binance client if not simulating (avoid pinging Binance on Streamlit)
client = None
if not simulate_flag:
    try:
        client = make_client(cfg)
    except Exception as e:
        st.warning("⚠️ Could not initialize Binance client. Running in simulation mode.")
        cfg.simulate = True

# UI starts here
st.title("💹 Binance Futures Trading Bot")

if simulate_flag:
    st.warning("⚠️ Running in simulation mode due to Binance API restrictions on Streamlit Cloud.")

st.sidebar.header("⚙️ Configuration")
simulate_ui = st.sidebar.checkbox("Simulation mode", value=cfg.simulate)
cfg.simulate = simulate_ui

st.markdown("### Select Order Type")
order_type = st.radio("Choose order type:", ["Market Order", "Limit Order"])

symbol = st.text_input("Enter Symbol (e.g., BTCUSDT):", "BTCUSDT")
side = st.selectbox("Select Side:", ["BUY", "SELL"])
quantity = st.text_input("Enter Quantity:", "0.001")

if order_type == "Market Order":
    if st.button("Place Market Order"):
        qty = validate_quantity(quantity)
        if not validate_symbol(symbol) or not validate_side(side) or qty is None:
            st.error("⚠️ Invalid inputs. Please check symbol, side, or quantity.")
        else:
            result = place_market_order(client, cfg, symbol, side, qty)
            st.success("✅ Market Order Executed!")
            st.json(result)

elif order_type == "Limit Order":
    price = st.text_input("Enter Limit Price:")
    tif = st.selectbox("Time In Force:", ["GTC", "IOC", "FOK"])
    if st.button("Place Limit Order"):
        qty = validate_quantity(quantity)
        try:
            price_f = float(price)
        except:
            st.error("⚠️ Invalid price")
            price_f = None

        if not validate_symbol(symbol) or not validate_side(side) or qty is None or price_f is None:
            st.error("⚠️ Invalid inputs.")
        else:
            result = place_limit_order(client, cfg, symbol, side, qty, price_f, tif)
            st.success("✅ Limit Order Executed!")
            st.json(result)
