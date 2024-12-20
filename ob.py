import requests
import pandas as pd

def obtener_order_book(symbol):
    url = "https://api.bybit.com/v5/market/orderbook"
    params = {
        "category": "spot",
        "symbol": symbol,
        "limit": 200
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data['result']

def calcular_liquidez_y_delta(order_book):
    bids = pd.DataFrame(order_book['b'], columns=['precio', 'cantidad']).astype(float)
    asks = pd.DataFrame(order_book['a'], columns=['precio', 'cantidad']).astype(float)
    
    liquidez_compras = (bids['precio'] * bids['cantidad']).sum()
    liquidez_ventas = (asks['precio'] * asks['cantidad']).sum()
    
    delta = liquidez_compras - liquidez_ventas
    
    return liquidez_compras, liquidez_ventas, delta

if __name__ == "__main__":
    symbol = "SOLUSDT"  # Reemplaza con el símbolo deseado
    order_book = obtener_order_book(symbol)
    liquidez_compras, liquidez_ventas, delta = calcular_liquidez_y_delta(order_book)
    
    print(f"Liquidez total en compras: {liquidez_compras:.2f} USDT")
    print(f"Liquidez total en ventas: {liquidez_ventas:.2f} USDT")
    print(f"Delta de liquidez: {delta:.2f} USDT")
    
    if delta > 0:
        print("Predominio de liquidez en compras.")
    elif delta < 0:
        print("Predominio de liquidez en ventas.")
    else:
        print("Equilibrio entre compras y ventas.")
