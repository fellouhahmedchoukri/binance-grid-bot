
import requests

def send_webhook(api_url, passphrase, symbol, action, high, low, steps):
    payload = {
        "passphrase": passphrase,
        "symbol": symbol,
        "action": action,
        "high_price": high,
        "low_price": low,
        "steps": steps
    }
    try:
        res = requests.post(api_url, json=payload)
        return res.json()
    except Exception as e:
        return {"success": False, "message": str(e)}

def fetch_balance(api_url, passphrase):
    try:
        res = requests.post(api_url, json={
            "passphrase": passphrase,
            "action": "balance"
        })
        return res.json()
    except Exception as e:
        return {"success": False, "message": str(e)}

def fetch_open_orders(api_url, passphrase):
    try:
        res = requests.post(api_url, json={
            "passphrase": passphrase,
            "action": "orders"
        })
        return res.json()
    except Exception as e:
        return {"success": False, "message": str(e)}
