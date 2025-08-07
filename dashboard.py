# dashboard.py

import streamlit as st
import requests
import os

st.set_page_config(page_title="Binance Grid Bot", layout="wide")

API_URL = os.getenv("API_URL", "https://binance-grid-bot-production.up.railway.app/webhook")
PASSPHRASE = os.getenv("WEBHOOK_PASSPHRASE", "#1960AlGeR@+=")

st.title("📈 Binance Grid Bot Dashboard")

with st.sidebar:
    st.header("⚙️ Paramètres")
    symbol = st.text_input("Symbole", "BTC:USDT")
    high_price = st.number_input("Prix haut", value=60000.0)
    low_price = st.number_input("Prix bas", value=55000.0)
    steps = st.slider("Niveaux de grille", min_value=3, max_value=20, value=9)
    action = st.selectbox("Action", ["entry", "exit", "grid_destroyed"])

    if st.button("🚀 Exécuter"):
        payload = {
            "passphrase": PASSPHRASE,
            "symbol": symbol,
            "action": action,
            "high_price": high_price,
            "low_price": low_price,
            "steps": steps
        }

        with st.spinner("Envoi de la requête..."):
            res = requests.post(API_URL, json=payload)
            if res.ok:
                st.success("✅ Requête envoyée avec succès")
                st.json(res.json())
            else:
                st.error(f"❌ Erreur {res.status_code}")
                st.text(res.text)

st.markdown("---")
st.subheader("🧾 Historique des requêtes (à implémenter)")
st.info("Tu peux ajouter un fichier `logs.json` ou une route `/status` pour afficher les ordres en cours.")
