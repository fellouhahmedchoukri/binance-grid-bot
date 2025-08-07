# exchange_utils.py

import ccxt
import logging
import config

logger = logging.getLogger(__name__)


def init_exchange():
    """
    Initialise et retourne une instance CCXT Binance en Spot ou Futures selon la config.
    """
    params = {
        "apiKey": config.API_KEY,
        "secret": config.API_SECRET,
        "enableRateLimit": True,
        "options": {"defaultType": config.EXCHANGE_TYPE},
    }
    exchange = ccxt.binance(params)

    if config.TEST_MODE:
        exchange.set_sandbox_mode(True)
        logger.info("MODE TEST ACTIVÉ - Transactions simulées")

    return exchange


def calculate_grid_levels(high: float, low: float, steps: int):
    """
    Retourne une liste de 'steps' niveaux linéaires entre high et low.
    """
    high, low = float(high), float(low)
    step_size = (high - low) / steps
    return [high - i * step_size for i in range(1, steps + 1)]


def place_grid_orders(exchange, symbol: str, high_price: float, low_price: float, steps: int):
    """
    Place une grille d'ordres limités 'buy' entre high_price et low_price.
    """
    try:
        grid_levels = calculate_grid_levels(high_price, low_price, steps)
        logger.info(f"Niveaux de grille: {grid_levels}")

        balance = exchange.fetch_balance()
        usdt_free = balance.get("USDT", {}).get("free", 0)
        logger.info(f"Solde USDT disponible: {usdt_free}")

        size_per_order = usdt_free * 0.20
        logger.info(f"Taille par ordre (20% du solde): {size_per_order} USDT")

        placed_orders = []
        exchange.load_markets()
        market = exchange.markets[symbol]
        price_prec = market["precision"]["price"]
        amount_prec = market["precision"]["amount"]

        for price in grid_levels:
            rounded_price = exchange.price_to_precision(symbol, price)
            amount = size_per_order / float(price)
            rounded_amount = exchange.amount_to_precision(symbol, amount)

            order = exchange.create_limit_buy_order(
                symbol=symbol,
                amount=rounded_amount,
                price=rounded_price,
            )
            logger.info(f"Ordre BUY placé @ {rounded_price} x {rounded_amount} | ID: {order['id']}")
            placed_orders.append(order)

        return {"success": True, "orders": placed_orders}

    except ccxt.InsufficientFunds as e:
        logger.error(f"Fonds insuffisants: {e}")
        return {"success": False, "message": "Fonds insuffisants"}
    except ccxt.InvalidOrder as e:
        logger.error(f"Ordre invalide: {e}")
        return {"success": False, "message": "Ordre invalide"}
    except Exception as e:
        logger.exception("Erreur place_grid_orders")
        return {"success": False, "message": str(e)}


def close_all_positions(exchange, symbol: str):
    """
    Annule tous les ordres et ferme la position ouverte sur symbol.
    """
    try:
        exchange.cancel_all_orders(symbol)
        logger.info("Tous les ordres annulés")

        balance = exchange.fetch_balance()
        base = symbol.split("/")[0]
        free_amount = balance.get(base, {}).get("free", 0)

        if free_amount > 0:
            rounded_amount = exchange.amount_to_precision(symbol, free_amount)
            order = exchange.create_market_sell_order(symbol, rounded_amount)
            logger.info(f"Position fermée: {rounded_amount} {base} | ID: {order['id']}")
            return {"success": True, "order": order}

        return {"success": True, "message": "Aucune position à fermer"}

    except Exception as e:
        logger.exception("Erreur close_all_positions")
        return {"success": False, "message": str(e)}
