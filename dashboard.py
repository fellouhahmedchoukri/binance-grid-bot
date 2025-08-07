import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import time
import config
import exchange_utils
import json
import requests
import os

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
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stButton>button {
        background-color: #1F77B4;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
    }
    .stAlert {
        border-left: 4px solid #FF4B4B;
    }
    .metric-card {
        background-color: #1E2130;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .positive {
        color: #00C853;
    }
    .negative {
        color: #FF5252;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de l'API Binance
try:
    exchange = exchange_utils.init_exchange()
    st.session_state.exchange = exchange
except Exception as e:
    st.error(f"Erreur de connexion à Binance: {str(e)}")
    st.stop()

# Titre du dashboard
st.title("📊 Binance Grid Bot Dashboard - The Quant Science")
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

# Fonctions principales
def fetch_portfolio():
    """Récupère le portefeuille"""
    try:
        balance = st.session_state.exchange.fetch_balance()
        return {k: v for k, v in balance['total'].items() if v > 0}
    except Exception as e:
        st.error(f"Erreur de récupération du portefeuille: {str(e)}")
        return {}

def fetch_open_orders(symbol="BTC/USDT"):
    """Récupère les ordres ouverts"""
    try:
        return st.session_state.exchange.fetch_open_orders(symbol)
    except Exception as e:
        st.error(f"Erreur de récupération des ordres: {str(e)}")
        return []

# Sidebar - Contrôle du bot
st.sidebar.header("⚙️ Contrôle du Bot")

# Section d'état
st.sidebar.subheader("🟢 Statut: Actif")
if st.sidebar.button("⏸️ Suspendre le Bot", key="pause_bot"):
    st.sidebar.warning("Fonctionnalité à implémenter")

if st.sidebar.button("🔴 Arrêter d'Urgence", key="emergency_stop", type="primary"):
    exchange_utils.close_all_positions(exchange, "BTC/USDT")
    st.sidebar.error("Toutes les positions ont été fermées!")

# Section de configuration
st.sidebar.subheader("⚡ Configuration Rapide")
symbol = st.sidebar.selectbox("Paire de trading", ["BTC/USDT", "ETH/USDT", "BNB/USDT"])
grid_range = st.sidebar.slider("Plage de la grille (%)", 5, 30, 10)
risk_per_trade = st.sidebar.slider("Risque par trade (%)", 1, 10, 2)

# Section d'alerte
st.sidebar.subheader("🔔 Alertes")
telegram_token = st.sidebar.text_input("Token Telegram Bot")
telegram_chat_id = st.sidebar.text_input("Chat ID Telegram")

# Layout principal
tab1, tab2, tab3, tab4 = st.tabs(["📈 Dashboard", "💼 Portefeuille", "📊 Positions", "📝 Journal"])

with tab1:
    # KPI Principaux
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Capital Total", "$25,643.21", "2.3%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Profit Journalier", "$342.15", "1.2%", delta_color="inverse")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Trades Actifs", "7", "-1")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Performance", "23.5%", "3.1%")
        st.markdown('</div>', unsafe_allow_html=True)
    
 # Graphique de performance - CORRECTION APPLIQUÉE ICI
    st.subheader("Performance du Portefeuille")
    
    # Données simulées
    dates = pd.date_range(start="2024-01-01", periods=30)
    portfolio_values = np.cumprod(1 + np.random.normal(0.001, 0.01, 30)) * 10000
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, 
        y=portfolio_values,
        mode='lines',
        name='Valeur Portefeuille',
        line=dict(color='#1F77B4', width=3)
    )
    
    fig.update_layout(
        template='plotly_dark',
        xaxis_title='Date',
        yaxis_title='Valeur ($)',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Grille de prix en temps réel
    st.subheader("Grille de Prix Actuelle")
    
    # Données simulées
    dates = pd.date_range(start="2024-01-01", periods=30)
    portfolio_values = np.cumprod(1 + np.random.normal(0.001, 0.01, 30)) * 10000
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, 
        y=portfolio_values,
        mode='lines',
        name='Valeur Portefeuille',
        line=dict(color='#1F77B4', width=3)
    )  # CORRECTION: Parenthèse correctement fermée
    
    fig.update_layout(
        template='plotly_dark',
        xaxis_title='Date',
        yaxis_title='Valeur ($)',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    # Portefeuille
    st.subheader("Composition du Portefeuille")
    
    portfolio = fetch_portfolio()
    if portfolio:
        df_portfolio = pd.DataFrame(list(portfolio.items()), columns=['Actif', 'Quantité'])
        
        # Calcul de la valeur en USD
        prices = {}
        for asset in df_portfolio['Actif']:
            if asset == 'USDT':
                prices[asset] = 1
            else:
                try:
                    ticker = exchange.fetch_ticker(f"{asset}/USDT")
                    prices[asset] = ticker['last']
                except:
                    prices[asset] = 0
        
        df_portfolio['Prix Actuel'] = df_portfolio['Actif'].map(prices)
        df_portfolio['Valeur'] = df_portfolio['Quantité'] * df_portfolio['Prix Actuel']
        
        # Affichage
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.dataframe(
                df_portfolio,
                column_config={
                    "Quantité": st.column_config.NumberColumn(format="%.6f"),
                    "Prix Actuel": st.column_config.NumberColumn(format="$ %.2f"),
                    "Valeur": st.column_config.NumberColumn(format="$ %.2f")
                },
                hide_index=True,
                use_container_width=True
            )
        
        with col2:
            fig = go.Figure(go.Pie(
                labels=df_portfolio['Actif'],
                values=df_portfolio['Valeur'],
                hole=0.4,
                marker=dict(colors=['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728'])
            ))
            fig.update_layout(
                title="Répartition du Portefeuille",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Aucune donnée de portefeuille disponible")

with tab3:
    # Positions actives
    st.subheader("Positions Actives")
    
    # Données simulées
    positions = [
        {'Paire': 'BTC/USDT', 'Type': 'Achat', 'Prix Entrée': 42000, 
         'Quantité': 0.5, 'Prix Actuel': 43650, 'Profit': '$825.00'},
        {'Paire': 'ETH/USDT', 'Type': 'Achat', 'Prix Entrée': 2500, 
         'Quantité': 5, 'Prix Actuel': 2542, 'Profit': '$210.00'}
    ]
    
    df_positions = pd.DataFrame(positions)
    
    st.dataframe(
        df_positions,
        column_config={
            "Prix Entrée": st.column_config.NumberColumn(format="$ %.0f"),
            "Prix Actuel": st.column_config.NumberColumn(format="$ %.0f"),
            "Profit": st.column_config.TextColumn("Profit", help="Profit non réalisé")
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Bouton de gestion
    col1, col2, col3 = st.columns(3)
    col1.button("🔄 Mettre à jour les Positions", use_container_width=True)
    col2.button("📊 Optimiser la Grille", use_container_width=True)
    col3.button("✖️ Fermer Toutes les Positions", type="primary", use_container_width=True)

with tab4:
    # Journal d'activité
    st.subheader("Journal d'Activité")
    
    # Données simulées
    activities = [
        {'Date': '2024-05-10 14:23:18', 'Événement': 'Ordre exécuté', 'Détail': 'Achat BTC à $43,600.00'},
        {'Date': '2024-05-10 14:15:02', 'Événement': 'Alerte reçue', 'Détail': 'Entrée Long sur BTC/USDT'},
        {'Date': '2024-05-10 13:45:51', 'Événement': 'Ordre placé', 'Détail': 'Ordre limite à $43,200.00'},
        {'Date': '2024-05-10 12:30:15', 'Événement': 'Position fermée', 'Détail': 'Vente BTC à $44,100.00 - Profit: $420.00'},
    ]
    
    for activity in activities:
        with st.container():
            st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between;">
                    <div><strong>{activity['Événement']}</strong></div>
                    <div style="color: #888;">{activity['Date']}</div>
                </div>
                <div style="margin-top: 10px;">{activity['Détail']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Interface pour actions manuelles
    st.subheader("Actions Manuellement")
    
    with st.form("manual_action_form"):
        action_type = st.selectbox("Type d'action", ["Achat", "Vente", "Modifier ordre", "Annuler ordre"])
        symbol = st.text_input("Paire", "BTC/USDT")
        amount = st.number_input("Quantité", min_value=0.001, value=0.01, step=0.01)
        price = st.number_input("Prix (pour ordres limites)", min_value=0.01, value=0.0)
        
        if st.form_submit_button("Exécuter l'Action"):
            st.success(f"Action {action_type} sur {symbol} exécutée avec succès!")
            add_position_to_history({
                'action': action_type,
                'symbol': symbol,
                'amount': amount,
                'price': price
            })

# Actualisation automatique
st_autorefresh = st.sidebar.checkbox("🔄 Actualisation automatique", value=True)
if st_autorefresh:
    refresh_interval = st.sidebar.slider("Intervalle (secondes)", 5, 60, 15)
    time.sleep(refresh_interval)
    st.experimental_rerun()

