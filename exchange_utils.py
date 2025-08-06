import ccxt
import config
import time
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_exchange():
    """Initialise la connexion à Binance"""
    exchange = ccxt.binance({
        'apiKey': config.API_KEY,
        'secret': config.API_SECRET,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    if config.TEST_MODE:
        exchange.set_sandbox_mode(True)
        logger.info("MODE TEST ACTIVÉ - Toutes les transactions sont simulées")
    
    return exchange

def calculate_grid_levels(high_price, low_price):
    """Calcule les niveaux de la grille selon votre stratégie"""
    grid_range = float(high_price) - float(low_price)
    grid_factor = grid_range / 9
    
    return {
        'grid_6': float(high_price) - (grid_factor * 5),
        'grid_7': float(high_price) - (grid_factor * 6),
        'grid_8': float(high_price) - (grid_factor * 7),
        'grid_9': float(high_price) - (grid_factor * 8),
        'grid_10': float(low_price)
    }

def place_grid_orders(exchange, symbol, high_price, low_price):
    """Place les ordres de la grille"""
    try:
        # Calcul des niveaux de grille
        grid_levels = calculate_grid_levels(high_price, low_price)
        logger.info(f"Niveaux de grille calculés: {grid_levels}")
        
        # Calcul de la taille des positions
        balance = exchange.fetch_balance()
        usdt_balance = balance['USDT']['free']
        logger.info(f"Solde USDT disponible: {usdt_balance}")
        
        # Calcul du montant par position (20% du solde par ordre)
        position_size_usdt = usdt_balance * 0.20
        logger.info(f"Montant par position: {position_size_usdt} USDT")
        
        # Placement des ordres
        for i, (level_name, price) in enumerate(grid_levels.items()):
            # Calcul de la quantité
            amount = position_size_usdt / price
            
            # Création de l'ordre limite
            order = exchange.create_limit_buy_order(
                symbol=symbol,
                amount=exchange.amount_to_precision(symbol, amount),
                price=exchange.price_to_precision(symbol, price)
            )
            
            logger.info(f"Ordre placé: {level_name} | Prix: {price} | Quantité: {amount:.6f} | ID: {order['id']}")
            
        return {"success": True, "message": "Grille placée avec succès"}
    
    except ccxt.InsufficientFunds as e:
        logger.error(f"Erreur de fonds insuffisants: {str(e)}")
        return {"success": False, "message": "Fonds insuffisants"}
    
    except Exception as e:
        logger.error(f"Erreur inattendue: {str(e)}")
        return {"success": False, "message": f"Erreur: {str(e)}"}

def close_all_positions(exchange, symbol):
    """Ferme toutes les positions et annule les ordres"""
    try:
        # Annulation de tous les ordres ouverts
        exchange.cancel_all_orders(symbol)
        logger.info("Tous les ordres annulés")
        
        # Fermeture des positions
        balance = exchange.fetch_balance()
        base_currency = symbol.split('/')[0]
        
        if balance.get(base_currency, {}).get('free', 0) > 0:
            amount = balance[base_currency]['free']
            exchange.create_market_sell_order(
                symbol=symbol,
                amount=exchange.amount_to_precision(symbol, amount)
            )
            logger.info(f"Position fermée: {amount} {base_currency}")
        
        return {"success": True, "message": "Positions fermées avec succès"}
    
    except Exception as e:
        logger.error(f"Erreur lors de la fermeture: {str(e)}")
        return {"success": False, "message": f"Erreur: {str(e)}"}
