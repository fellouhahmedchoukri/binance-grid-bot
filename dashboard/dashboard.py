import streamlit as st
from utils import send_webhook, fetch_balance, fetch_open_orders

st.set_page_config(page_title="Binance Grid Bot", layout="wide")
st.title("📈 Binance Grid Bot Dashboard")

API_URL = st.secrets.get("API_URL", "https://binance-grid-bot-production.up.railway.app/webhook")
PASSPHRASE = st.secrets.get("WEBHOOK_PASSPHRASE", "#1960AlGeR@+=")

tab1, tab2, tab3 = st.tabs(["🎛️ Contrôle", "💰 Solde", "📋 Ordres ouverts"])

with tab1:
    st.subheader("📤 Envoi manuel de webhook")
    symbol = st.text_input("Symbole", "BTC:USDT")
    high_price = st.number_input("Prix haut", value=60000.0)
    low_price = st.number_input("Prix bas", value=55000.0)
    steps = st.slider("Niveaux de grille", min_value=3, max_value=20, value=9)
    action = st.selectbox("Action", ["entry", "exit", "grid_destroyed"])

    if st.button("🚀 Exécuter"):
        result = send_webhook(API_URL, PASSPHRASE, symbol, action, high_price, low_price, steps)
        if result.get("success"):
            st.success("✅ Webhook envoyé")
        else:
            st.error("❌ Échec")
        st.json(result)

with tab2:
    st.subheader("💰 Solde Binance")
    if st.button("🔄 Rafraîchir solde"):
        balance = fetch_balance(API_URL, PASSPHRASE)
        st.json(balance)

with tab3:
    st.subheader("📋 Ordres ouverts")
    if st.button("🔄 Rafraîchir ordres"):
        orders = fetch_open_orders(API_URL, PASSPHRASE)
        st.json(orders)
