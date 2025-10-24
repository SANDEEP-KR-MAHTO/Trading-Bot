import streamlit as st
from dotenv import load_dotenv
import os
from src.common import BotConfig, make_client, logger, validate_symbol, validate_side, validate_quantity
from src.market_orders import place_market_order
from src.limit_orders import place_limit_order

# Load environment variables
load_dotenv()


api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# Force simulation mode on Streamlit Cloud
is_cloud = os.getenv("STREAMLIT_RUNTIME", "") != ""
simulate_flag = True if is_cloud else (os.getenv("SIMULATE", "0") == "1")

cfg = BotConfig(api_key, api_secret, testnet=True, simulate=simulate_flag)
client = None if simulate_flag else make_client(cfg)

if simulate_flag:
    st.warning("⚠️ Running in simulation mode due to API region restrictions.")


# App title
st.title("💹 Binance Futures Trading Bot (Testnet)")

st.sidebar.header("⚙️ Configuration")
simulate_ui = st.sidebar.checkbox("Run in simulation mode", value=simulate_flag)
cfg.simulate = simulate_ui

st.markdown("### Select Order Type")
order_type = st.radio("Choose an order type:", ["Market Order", "Limit Order"])

symbol = st.text_input("Enter Symbol (e.g., BTCUSDT):", "BTCUSDT")
side = st.selectbox("Select Side:", ["BUY", "SELL"])
quantity = st.text_input("Enter Quantity:", "0.001")

if order_type == "Market Order":
    if st.button("Place Market Order"):
        qty = validate_quantity(quantity)
        if not validate_symbol(symbol) or not validate_side(side) or qty is None:
            st.error("⚠️ Invalid inputs. Please check symbol, side, or quantity.")
        else:
            try:
                result = place_market_order(client, cfg, symbol, side, qty)
                st.success("✅ Market Order Placed Successfully!")
                st.json(result)
            except Exception as e:
                st.error(f"Error: {e}")

elif order_type == "Limit Order":
    price = st.text_input("Enter Limit Price:")
    time_in_force = st.selectbox("Time In Force:", ["GTC", "IOC", "FOK"])
    if st.button("Place Limit Order"):
        qty = validate_quantity(quantity)
        try:
            price_f = float(price)
        except:
            st.error("⚠️ Invalid price")
            price_f = None

        if not validate_symbol(symbol) or not validate_side(side) or qty is None or price_f is None:
            st.error("⚠️ Invalid inputs. Please check all fields.")
        else:
            try:
                result = place_limit_order(client, cfg, symbol, side, qty, price_f, time_in_force)
                st.success("✅ Limit Order Placed Successfully!")
                st.json(result)
            except Exception as e:
                st.error(f"Error: {e}")
