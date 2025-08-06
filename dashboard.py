import streamlit as st

st.set_page_config(
    page_title="Binance Grid Bot Dashboard",
    layout="wide"
)

st.title("Binance Grid Bot Dashboard")
st.success("L'application démarre correctement!")

# Vérification des dépendances
try:
    import pandas as pd
    import plotly
    import ccxt
    st.info("Toutes les dépendances sont installées avec succès!")
except ImportError as e:
    st.error(f"Erreur d'importation: {str(e)}")
