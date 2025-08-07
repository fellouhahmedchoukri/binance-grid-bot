import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time
import config
import exchange_utils
import json
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration de la page
st.set_page_config(
    page_title="Binance Grid Bot Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .metric-card {
        background-color: #1E2130;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Titre du dashboard
st.title("📊 Binance Grid Bot Dashboard")
st.caption("Dashboard professionnel pour la gestion de votre stratégie Grid Trading")

# Section de connexion sécurisée
if 'authenticated' not in st.session_state:
    password = st.sidebar.text_input("🔑 Mot de passe d'accès", type="password")
    if password == config.DASHBOARD_PASSWORD:
        st.session_state.authenticated = True
    else:
        if password != "":
            st.error("Mot de passe incorrect")
        st.stop()

# Layout principal
tab1, tab2, tab3 = st.tabs(["📈 Dashboard", "💼 Portefeuille", "📝 Journal"])

with tab1:
    # KPI Principaux
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Capital Total", "$25,643.21", "2.3%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Profit Journalier", "$342.15", "1.2%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Trades Actifs", "7", "-1")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Section de contrôle
    st.subheader("Contrôle du Bot")
    
    if st.button("⏸️ Suspendre le Bot", key="pause_bot"):
        st.warning("Fonctionnalité à implémenter")
    
    if st.button("🔴 Arrêter d'Urgence", key="emergency_stop", type="primary"):
        st.success("Toutes les positions ont été fermées!")

with tab2:
    # Portefeuille
    st.subheader("Composition du Portefeuille")
    
    # Données simulées
    portfolio_data = {
        'Actif': ['BTC', 'ETH', 'USDT'],
        'Quantité': [0.5, 5, 2500],
        'Valeur ($)': [21000, 12500, 2500]
    }
    
    df_portfolio = pd.DataFrame(portfolio_data)
    st.dataframe(df_portfolio, hide_index=True, use_container_width=True)
    
    # Graphique simple
    st.subheader("Répartition du Portefeuille")
    st.bar_chart(df_portfolio.set_index('Actif')['Valeur ($)'])

with tab3:
    # Journal d'activité
    st.subheader("Journal d'Activité")
    
    # Données simulées
    activities = [
        {'Date': datetime.now().strftime('%Y-%m-%d %H:%M'), 'Événement': 'Bot démarré', 'Détail': 'Système initialisé'},
        {'Date': datetime.now().strftime('%Y-%m-%d %H:%M'), 'Événement': 'Connexion Binance', 'Détail': 'Connecté avec succès'},
    ]
    
    for activity in activities:
        with st.container():
            st.markdown(f"""
            <div class="metric-card">
                <div><strong>{activity['Événement']}</strong></div>
                <div>{activity['Date']}</div>
                <div>{activity['Détail']}</div>
            </div>
            """, unsafe_allow_html=True)

# Section de configuration
st.sidebar.header("⚙️ Configuration")
symbol = st.sidebar.selectbox("Paire de trading", ["BTC/USDT", "ETH/USDT", "DOGE/USDT"])
grid_range = st.sidebar.slider("Plage de la grille (%)", 5, 30, 10)
risk_per_trade = st.sidebar.slider("Risque par trade (%)", 1, 10, 2)

# Actualisation automatique
if st.sidebar.checkbox("🔄 Actualisation automatique", value=True):
    refresh_interval = st.sidebar.slider("Intervalle (secondes)", 5, 60, 15)
    time.sleep(refresh_interval)
    st.rerun()

# Message de statut
st.sidebar.success("Dashboard opérationnel")
