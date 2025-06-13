import traci
import socket
import json
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd

TCP_IP = '127.0.0.1'
TCP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.connect((TCP_IP, TCP_PORT))
    print("Connected to Unity TCP server at 127.0.0.1:5005")
except socket.error as e:
    print(f"Failed to connect to Unity: {e}")
    exit(1)


# Connect to SUMO and start the simulation
traci.start(['sumo-gui', '-c', 'C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/sumotest.sumo.cfg', '--emission-output', 'emission_output.xml'])
step = 0
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    # Get a list of all vehicles currently in the simulation
    vehicles = traci.vehicle.getIDList()
    vehicle_data_list = []
    for vehicle_id in vehicles:
        real_id = vehicle_id.split(' ')[0]
        data = {
                "id": real_id,
                "x": traci.vehicle.getPosition(vehicle_id)[0],
                "y": traci.vehicle.getPosition(vehicle_id)[1],
                "angle": traci.vehicle.getAngle(vehicle_id),
                "speed": traci.vehicle.getSpeed(vehicle_id),
                "CO2": traci.vehicle.getCO2Emission(vehicle_id),
                "CO": traci.vehicle.getCOEmission(vehicle_id),
                "HC": traci.vehicle.getHCEmission(vehicle_id),
                "NOx": traci.vehicle.getNOxEmission(vehicle_id),
                "PMx": traci.vehicle.getPMxEmission(vehicle_id),
                "fuel": traci.vehicle.getFuelConsumption(vehicle_id),
                "electricity": traci.vehicle.getElectricityConsumption(vehicle_id),
                "noise": traci.vehicle.getNoiseEmission(vehicle_id),
                "priority": 0,
            }
        vehicle_data_list.append(data)

        try:
            message = json.dumps(vehicle_data_list).encode('utf-8')
            sock.sendall(message)
        except Exception as e:
            print(f"Send failed: {e}")
    step += 1
    time.sleep(0.03)  # optional pacing

# Stop the simulation and close the TraCI connection
traci.close()
sock.close()
print("Disconnected from Unity TCP server")
