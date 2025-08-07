# config.py

import os
from dotenv import load_dotenv

# Charger le .env
load_dotenv()

# Clés API Binance
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# Passphrase pour sécuriser le webhook
WEBHOOK_PASSPHRASE = os.getenv("WEBHOOK_PASSPHRASE")

# Secret pour la signature HMAC
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

# Mode test (True pour sandbox CCXT)
TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"

# Type d'échange: "spot" ou "future"
EXCHANGE_TYPE = os.getenv("EXCHANGE_TYPE", "spot")

# Nombre de niveaux de grille par défaut
GRID_STEPS = int(os.getenv("GRID_STEPS", 9))

# Vérification des variables essentielles
required = ["API_KEY", "API_SECRET", "WEBHOOK_PASSPHRASE", "WEBHOOK_SECRET"]
missing = [var for var in required if os.getenv(var) is None]
if missing:
    raise EnvironmentError(f"Variables d'environnement manquantes: {', '.join(missing)}")
