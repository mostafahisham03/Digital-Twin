import socket
import json
import time

HOST = '127.0.0.1'
PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
print("Connected to server")

for i in range(5):
    data = {
        "id": f"veh{i}",
        "x": 100 + i * 5,
        "y": 200 + i * 3,
        "angle": i * 10,
        "speed": 15 + i,
        "CO2": 12 + i,
        "CO": 0.3 + i * 0.01,
        "HC": 0.02 + i * 0.001,
        "NOx": 0.1 + i * 0.01,
        "PMx": 0.005 + i * 0.0005,
        "fuel": 0.4 + i * 0.05,
        "electricity": 0.0,
        "noise": 70 + i
    }
    message = json.dumps(data).encode('utf-8')
    sock.sendall(message)
    time.sleep(0.000001)

sock.close()
