# config.py

import os
from dotenv import load_dotenv

# Charge les variables depuis .env
load_dotenv()

API_KEY         = os.getenv("API_KEY")
API_SECRET      = os.getenv("API_SECRET")
WEBHOOK_PASSPHRASE = os.getenv("WEBHOOK_PASSPHRASE")
TEST_MODE       = os.getenv("TEST_MODE", "true").lower() == "true"
EXCHANGE_TYPE   = os.getenv("EXCHANGE_TYPE", "spot")
GRID_STEPS      = int(os.getenv("GRID_STEPS", 9))
LOG_LEVEL       = os.getenv("LOG_LEVEL", "INFO")
PORT            = int(os.getenv("PORT", 5000))

# Vérification des variables critiques
_missing = [v for v in ("API_KEY","API_SECRET","WEBHOOK_PASSPHRASE") if not globals()[v]]
if _missing:
    raise EnvironmentError(f"Variables manquantes: {', '.join(_missing)}")
