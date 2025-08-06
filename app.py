from flask import Flask, request, jsonify
import config
import exchange_utils
import json
import logging
import os

app = Flask(__name__)

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.route("/")
def home():
    return "<h1>Binance Grid Bot - The Quant Science</h1><p>Service opérationnel</p>"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Parse les données JSON
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Données JSON invalides"}), 400
        
        logger.info(f"Requête reçue: {json.dumps(data, indent=2)}")
        
        # Vérification de la passphrase
        if data.get("passphrase") != config.WEBHOOK_PASSPHRASE:
            logger.warning("Passphrase invalide reçue")
            return jsonify({"success": False, "message": "Passphrase invalide"}), 401
        
        # Initialisation de l'API Binance
        exchange = exchange_utils.init_exchange()
        symbol = data['symbol'].replace(":", "/")  # Format: BTC/USDT
        
        # Traitement des actions
        action = data['action']
        
        if action == "entry":
            # Vérification des paramètres requis
            if 'high_price' not in data or 'low_price' not in data:
                return jsonify({
                    "success": False,
                    "message": "Paramètres manquants: high_price et low_price requis"
                }), 400
                
            result = exchange_utils.place_grid_orders(
                exchange,
                symbol,
                data['high_price'],
                data['low_price']
            )
            return jsonify(result)
        
        elif action == "exit" or action == "grid_destroyed":
            result = exchange_utils.close_all_positions(exchange, symbol)
            return jsonify(result)
        
        else:
            return jsonify({
                "success": False,
                "message": f"Action non reconnue: {action}"
            }), 400
    
    except Exception as e:
        logger.error(f"Erreur globale: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Erreur serveur: {str(e)}"
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  # Port codé en dur
