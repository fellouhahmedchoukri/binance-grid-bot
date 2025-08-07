# exchange_utils.py

import ccxt
import logging
import config

logger = logging.getLogger(__name__)

def init_exchange():
    """
    Initialise CCXT Binance en spot ou futures selon EXCHANGE_TYPE.
    """
    params = {
        "apiKey": config.API_KEY,
        "secret": config.API_SECRET,
        "enableRateLimit": True,
        "options": {"defaultType": config.EXCHANGE_TYPE}
    }
    exchange = ccxt.binance(params)
    if config.TEST_MODE:
        exchange.set_sandbox_mode(True)
        logger.info("MODE TEST ACTIVÉ (sandbox)")
    return exchange

def calculate_grid_levels(high, low, steps):
    """
    Retourne une liste de `steps` prix linéaires entre high et low.
    """
    high, low = float(high), float(low)
    step = (high - low) / steps
    return [high - i * step for i in range(1, steps + 1)]

def place_grid_orders(exchange, symbol, high_price, low_price, steps):
    """
    Place une grille d'ordres buy limités.
    """
    try:
        exchange.load_markets()
        grid = calculate_grid_levels(high_price, low_price, steps)
        logger.info(f"Niveaux de grille : {grid}")

        balance = exchange.fetch_balance()
        usdt_free = balance.get("USDT", {}).get("free", 0)
        logger.info(f"USDT libre : {usdt_free}")

        qty_per_order = usdt_free * 0.20
        logger.info(f"Montant par ordre : {qty_per_order} USDT")

        orders = []
        market = exchange.markets[symbol]
        for price in grid:
            price_str = exchange.price_to_precision(symbol, price)
            amount = qty_per_order / float(price)
            amount_str = exchange.amount_to_precision(symbol, amount)

            order = exchange.create_limit_buy_order(
                symbol=symbol,
                amount=amount_str,
                price=price_str
            )
            logger.info(f"Ordre BUY @ {price_str} x {amount_str} | ID {order['id']}")
            orders.append(order)

        return {"success": True, "orders": orders}

    except ccxt.InsufficientFunds:
        logger.error("Fonds insuffisants")
        return {"success": False, "message": "Fonds insuffisants"}
    except Exception as e:
        logger.exception("Erreur place_grid_orders")
        return {"success": False, "message": str(e)}

def close_all_positions(exchange, symbol):
    """
    Annule tous les ordres et ferme la position spot.
    """
    try:
        exchange.cancel_all_orders(symbol)
        logger.info("Annulation de tous les ordres")

        balance = exchange.fetch_balance()
        base = symbol.split("/")[0]
        free_amt = balance.get(base, {}).get("free", 0)
        if free_amt > 0:
            amt_str = exchange.amount_to_precision(symbol, free_amt)
            order = exchange.create_market_sell_order(symbol, amt_str)
            logger.info(f"Vente marché {amt_str} {base} | ID {order['id']}")
            return {"success": True, "order": order}

        return {"success": True, "message": "Aucune position à fermer"}
    except Exception as e:
        logger.exception("Erreur close_all_positions")
        return {"success": False, "message": str(e)}
