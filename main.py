import websocket
import json
import redis
from datetime import datetime, timedelta


url = "wss://stream.bybit.com/v5/public/spot"
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

redis_key = "orderbook_deltas"

def almacenar_delta(data):
    timestamp = data['cts']
    entry = {
        "timestamp": timestamp,
        "bids": data['data'].get('b', []),
        "asks": data['data'].get('a', [])
    }
    redis_client.zadd(redis_key, {json.dumps(entry): timestamp})
    hace_15_minutos = int((datetime.utcnow() - timedelta(minutes=15)).timestamp() * 1000)
    redis_client.zremrangebyscore(redis_key, '-inf', hace_15_minutos)

def consultar_deltas_recientes():
    ahora = int(datetime.utcnow().timestamp() * 1000)
    hace_15_minutos = int((datetime.utcnow() - timedelta(minutes=15)).timestamp() * 1000)
    return redis_client.zrangebyscore(redis_key, hace_15_minutos, ahora)


def on_message(ws, message):
    data = json.loads(message)
    if 'topic' in data and 'orderBook' in data['topic']:
        almacenar_delta(data)
        print("Delta almacenado")
        recientes = consultar_deltas_recientes()
        print(f"Últimos deltas (15 minutos): {len(recientes)}")


def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"Conexión cerrada: Código {close_status_code}, Mensaje: {close_msg}")

def on_open(ws):
    subscribe_message = {
        "op": "subscribe",
        "args": ["orderbook.1.BTCUSDT"]
    }
    ws.send(json.dumps(subscribe_message))
    print("Suscripción enviada.")

ws = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error, on_close=on_close)
ws.on_open = on_open

while True:
    try:
        ws.run_forever()
    except Exception as e:
        print(f"Reconectando debido a: {e}")
