import os
from flask import Flask, request, jsonify
import ccxt

app = Flask(__name__)

# Charge tes clés Binance depuis les variables d’environnement
API_KEY = os.environ.get("BINANCE_API_KEY")
API_SECRET = os.environ.get("BINANCE_API_SECRET")
PASSPHRASE = os.environ.get("WEBHOOK_PASSPHRASE")

# Initialise l’exchange CCXT
exchange = ccxt.binance({
    "apiKey": API_KEY,
    "secret": API_SECRET,
    "enableRateLimit": True,
})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"success": False, "message": "No JSON payload"}), 400

    # Vérifie la passphrase
    if data.get("passphrase") != PASSPHRASE:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    symbol = data.get("symbol")
    action = data.get("action")

    try:
        # 1. Entrée en grille
        if action == "entry":
            high_price = float(data["high_price"])
            low_price = float(data["low_price"])
            steps = int(data["steps"])
            # Ta logique de création de grille ici…
            # Exemple simplifié :
            orders = build_grid_and_place_orders(symbol, low_price, high_price, steps)
            return jsonify({"success": True, "orders": orders}), 200

        # 2. Sortie partielle / totale
        elif action == "exit":
            # Ta logique d’exit ici…
            result = close_grid_positions(symbol)
            return jsonify({"success": True, "result": result}), 200

        # 3. Destruction de grille manuelle
        elif action == "grid_destroyed":
            # Ta logique de destruction de grille ici…
            result = destroy_grid(symbol)
            return jsonify({"success": True, "result": result}), 200

        # 4. Récupérer le solde
        elif action == "balance":
            balance = exchange.fetch_balance()
            return jsonify({"success": True, "balance": balance}), 200

        # 5. Récupérer les ordres ouverts
        elif action == "orders":
            if not symbol:
                return jsonify({"success": False, "message": "symbol is required for orders"}), 400
            orders = exchange.fetch_open_orders(symbol)
            return jsonify({"success": True, "orders": orders}), 200

        # Action inconnue
        else:
            return jsonify({"success": False, "message": f"Unknown action `{action}`"}), 400

    except Exception as e:
        # Logue l’erreur en prod, ici on renvoie juste le message
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
