import os
from flask import Flask, request, jsonify
import ccxt

app = Flask(__name__)

# Endpoint GET pour Render
@app.route("/", methods=["GET"])
def home():
    return "Binance Grid Bot is running!", 200

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

    if data.get("passphrase") != PASSPHRASE:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    symbol = data.get("symbol")
    action = data.get("action")

    try:
        if action == "entry":
            high_price = float(data["high_price"])
            low_price = float(data["low_price"])
            steps = int(data["steps"])
            orders = build_grid_and_place_orders(symbol, low_price, high_price, steps)
            return jsonify({"success": True, "orders": orders}), 200

        elif action == "exit":
            result = close_grid_positions(symbol)
            return jsonify({"success": True, "result": result}), 200

        elif action == "grid_destroyed":
            result = destroy_grid(symbol)
            return jsonify({"success": True, "result": result}), 200

        elif action == "balance":
            balance = exchange.fetch_balance()
            return jsonify({"success": True, "balance": balance}), 200

        elif action == "orders":
            if not symbol:
                return jsonify({"success": False, "message": "symbol is required for orders"}), 400
            orders = exchange.fetch_open_orders(symbol)
            return jsonify({"success": True, "orders": orders}), 200

        else:
            return jsonify({"success": False, "message": f"Unknown action `{action}`"}), 400

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Démarrage local (non utilisé par Render)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
