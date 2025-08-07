# app.py

import os
import json
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

import config
import exchange_utils

# Charge .env
load_dotenv()

# Configuration du logger
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "<h1>Binance Grid Bot</h1><p>Service opérationnel</p>"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        logger.info(f"Payload reçu : {json.dumps(data)}")

        # Vérification de la passphrase
        if data.get("passphrase") != config.WEBHOOK_PASSPHRASE:
            logger.warning("Passphrase invalide")
            return jsonify({"success": False, "message": "Passphrase invalide"}), 401

        # Champs indispensables
        symbol = data.get("symbol")
        action = data.get("action")
        if not symbol or not action:
            return jsonify({"success": False, "message": "symbol et action requis"}), 400

        symbol = symbol.replace(":", "/")  # ex. "BTC:USDT" → "BTC/USDT"
        exchange = exchange_utils.init_exchange()

        if action == "entry":
            if "high_price" not in data or "low_price" not in data:
                return jsonify({
                    "success": False,
                    "message": "high_price et low_price requis pour entry"
                }), 400

            result = exchange_utils.place_grid_orders(
                exchange,
                symbol,
                data["high_price"],
                data["low_price"],
                steps=data.get("steps", config.GRID_STEPS)
            )
            return jsonify(result), 200

        elif action in ("exit", "grid_destroyed"):
            result = exchange_utils.close_all_positions(exchange, symbol)
            return jsonify(result), 200

        else:
            return jsonify({
                "success": False,
                "message": f"Action non reconnue: {action}"
            }), 400

    except Exception as e:
        logger.exception("Erreur serveur")
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=config.PORT,
        debug=(os.getenv("FLASK_ENV") == "development")
    )
