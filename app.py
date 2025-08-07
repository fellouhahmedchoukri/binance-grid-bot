# app.py

from flask import Flask, request, jsonify
import os
import json
import logging
import hmac
import hashlib
from dotenv import load_dotenv

import exchange_utils
import config

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def verify_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    """
    Vérifie la signature HMAC SHA256 du payload.
    """
    computed = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature)


@app.route("/", methods=["GET"])
def home():
    return "<h1>Binance Grid Bot - The Quant Science</h1><p>Service opérationnel</p>"


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        raw_body = request.data
        signature = request.headers.get("X-Signature", "")

        # Vérification de la signature HMAC
        if not verify_signature(raw_body, signature, config.WEBHOOK_SECRET):
            logger.warning("Signature invalide")
            return jsonify({"success": False, "message": "Signature invalide"}), 401

        # Parser le JSON
        data = request.get_json(force=True)
        logger.info(f"Payload reçu: {json.dumps(data, indent=2)}")

        # Validation minimale du schéma
        for field in ("passphrase", "symbol", "action"):
            if field not in data:
                return jsonify({"success": False, "message": f"Champ manquant: {field}"}), 400

        if data["passphrase"] != config.WEBHOOK_PASSPHRASE:
            logger.warning("Passphrase invalide")
            return jsonify({"success": False, "message": "Passphrase invalide"}), 401

        symbol = data["symbol"].replace(":", "/")
        action = data["action"]

        # Initialisation de l'API (Spot ou Futures)
        exchange = exchange_utils.init_exchange()

        if action == "entry":
            for param in ("high_price", "low_price"):
                if param not in data:
                    return jsonify({"success": False, "message": f"Champ manquant: {param}"}), 400

            result = exchange_utils.place_grid_orders(
                exchange,
                symbol,
                data["high_price"],
                data["low_price"],
                steps=int(data.get("steps", config.GRID_STEPS)),
            )
            return jsonify(result), 200

        elif action in ("exit", "grid_destroyed"):
            result = exchange_utils.close_all_positions(exchange, symbol)
            return jsonify(result), 200

        else:
            return jsonify({"success": False, "message": f"Action non reconnue: {action}"}), 400

    except Exception as e:
        logger.exception("Erreur serveur")
        return jsonify({"success": False, "message": f"Erreur serveur: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
