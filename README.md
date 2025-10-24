# 💹 Binance Futures Trading Bot (Python + Streamlit)

A simple, modular, and testnet-safe **Binance Futures Trading Bot** built with Python.  
Supports **Market**, **Limit**, and **TWAP** orders — with a clean **Streamlit web UI** for easy interaction.

---

## 🚀 Features

- 🧠 Modular architecture (Market, Limit, TWAP orders)
- 💻 Streamlit UI — trade from your browser
- 🔐 `.env` file support for API keys (using `python-dotenv`)
- 🧾 Centralized logging (`bot.log`)
- 🧪 Simulation mode for safe testing
- ⚙️ Built on **Binance Futures Testnet**

---

## 🗂️ Project Structure
```bash

binance-futures-bot/
|
├── app.py
├── requirements.txt
├── .gitignore 
├── .env.example
|      
├── src/
│   └── common.py
│   └── market_orders.py
|   └── limit_orders.py
|
├── src/advanced/
│           └── twap.py
|           └── oco_sim.py 
|       
└── README.md

```



## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/binance-futures-bot.git
cd binance-futures-bot
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate        # On Windows
# or
source venv/bin/activate     # On Mac/Linux
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
### 4️⃣ Configure Environment Variables
Create a `.env` file in the project root:
```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_secret_key_here
SIMULATE=0   # 1 = simulate mode, 0 = real testnet
```


### ⚡ Running from CLI
```bash
python -m src.market_orders BTCUSDT BUY 0.001
python -m src.limit_orders BTCUSDT SELL 0.001 70000
python -m src.advanced.twap BTCUSDT BUY 0.05 5 60
```

### 🧠 Example Output
```bash 
INFO binance_bot - Starting TWAP: BTCUSDT BUY total_qty=0.05 chunks=5 interval=12.00
INFO binance_bot - TWAP chunk 1/5: placing market order qty=0.01
INFO binance_bot - API action=futures_create_order ...
``` 
### 🧰 Tech Stack
- Python 3.9+

- Streamlit — UI

- python-binance — Binance API client

- python-dotenv — Environment management
 
### 🧪 Testing in Simulation Mode
```bash
python -m src.market_orders BTCUSDT BUY 0.001 --simulate
``` 
### 🧩 License
This project is open-source and available under the MIT License.


### 💡 Running the Streamlit UI
```bash
streamlit run app.py
```
### 📷 ScreenShots
<img width="1900" height="815" alt="image" src="https://github.com/user-attachments/assets/e3c7a654-deed-4081-baae-4ee37554779c" />
<img width="1905" height="846" alt="image" src="https://github.com/user-attachments/assets/7afb1e47-a47c-43b7-a1bf-b13a6480d1ef" />




### 🧮 Live Demo
-👉 [Click here for Live Demo](https://trading-bot-8zu9gsvgmfwwxxvnxlwxdu.streamlit.app/)
