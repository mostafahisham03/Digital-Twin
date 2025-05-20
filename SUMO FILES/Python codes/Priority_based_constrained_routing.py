import traci
import socket
import json
import time
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors

TCP_IP = '127.0.0.1'
TCP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.connect((TCP_IP, TCP_PORT))
    print("Connected to Unity TCP server at 127.0.0.1:5005")
except socket.error as e:
    print(f"Failed to connect to Unity: {e}")
    exit(1)


df = pd.read_excel('C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/Dataset.xlsx')

# Preprocessing: split dataset into features and target variable
X = df.drop(['priority'], axis=1) # features (exclude 'priority')
y = df['priority'] # target variable 
X.drop('initial priority', axis=1, inplace=True)
# Creating the Random Forest model with default parameters
rf_model = RandomForestRegressor()

# Training the model on the entire dataset
rf_model.fit(X, y)


# Connect to SUMO and start the simulation
# traci.start(['sumo-gui', '-c', 'C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/Testing Scenarios/sumotesting.sumo.cfg'])
traci.start(['sumo-gui', '-c', 'C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/sumotest.sumo.cfg', '--emission-output', 'emission_output.xml', '--step-length', '0.5'])
# traci.start(['sumo-gui', '-c', 'C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/new test/sumotest2.sumo.cfg'])













import xml.etree.ElementTree as ET
import random
# finding all the edges in the network
def parse_edge_variables(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    edge_variables = []
    for edge in root.findall(".//edge"):
        edge_id = edge.get("id")
        from_node = edge.get("from")
        to_node = edge.get("to")

        if edge_id is not None and from_node is not None and to_node is not None:
            edge_variables.append((edge_id, from_node, to_node))

    return edge_variables
# randomly choosing an edge the vehicle will be able to take on the next junction
def random_next_edge(startEdge,network_file_path):
    edge_vars = parse_edge_variables(network_file_path)
    current_edge = next((edge for edge in edge_vars if edge[0] == startEdge), None)
    if current_edge is not None:
        next_edges = [edge for edge in edge_vars if edge[1] == current_edge[2] and edge[2] != current_edge[1]]
        if next_edges is not None:
            random_edge = random.choice(next_edges)[0]
            return random_edge
        else:
            return None
    else:
        return None

def get_total_emission(edge_id):
    try:
        co2 = traci.edge.getCO2Emission(edge_id)
        co = traci.edge.getCOEmission(edge_id)
        nox = traci.edge.getNOxEmission(edge_id)
        pmx = traci.edge.getPMxEmission(edge_id)
        hc = traci.edge.getHCEmission(edge_id)
        fuel = traci.edge.getFuelConsumption(edge_id)
        return co2 + co + nox + pmx + hc + fuel
    except:
        return 0.0
    
def get_color_from_value(value, min_val=0, max_val=10000):
    norm = colors.Normalize(vmin=min_val, vmax=max_val)
    cmap = cm.get_cmap('Reds')
    rgba = cmap(norm(value))
    return tuple(int(255 * x) for x in rgba[:3])







step = 0
priorities = {}
while traci.simulation.getMinExpectedNumber() > 0 and step<10000:
    for _ in range(30):
        traci.simulationStep()
        
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
                "priority": priorities.get(vehicle_id.split()[0], 0),
            }
            vehicle_data_list.append(data)

        try:
            print(vehicle_data_list)
            message = json.dumps(vehicle_data_list).encode('utf-8')
            sock.sendall(message)
        except Exception as e:
            print(f"Send failed: {e}")
        
        step += 1
        time.sleep(0.03)  # optional pacing

    for edge_id in traci.edge.getIDList():
        try:
            total_emission = get_total_emission(edge_id)
            if(total_emission > 0):
             traci.edge.setColor(edge_id, (255, 0, 0))
        except:
            continue
    # Get a list of all vehicles currently in the simulation
    vehicles = traci.vehicle.getIDList()
    start_positions ={}
    AllVehicles =[]
    for vehicle_id in vehicles:
        print(traci.vehicle.getRoute(vehicle_id))
        # Extract features from the current vehicle
        CO2 = traci.vehicle.getCO2Emission(vehicle_id)
        CO = traci.vehicle.getCOEmission(vehicle_id)
        HC = traci.vehicle.getHCEmission(vehicle_id)
        NOx = traci.vehicle.getNOxEmission(vehicle_id)
        PMx = traci.vehicle.getPMxEmission(vehicle_id)
        fuel = traci.vehicle.getFuelConsumption(vehicle_id)
        electricity = traci.vehicle.getElectricityConsumption(vehicle_id)
        noise = traci.vehicle.getNoiseEmission(vehicle_id)
        features = [CO2,CO,HC,NOx,PMx,fuel,electricity,noise,0,0]
        print("Features: ",features)
        # Predict the priority using the Random Forest model
        priority = rf_model.predict([features])[0]
        print("Predicted Priority of vehicle with id {}: {}".format(vehicle_id, priority))
        priorities[vehicle_id] = priority
        current_edge = traci.vehicle.getRoadID(vehicle_id)
        route = traci.vehicle.getRoute(vehicle_id)
        
        # data to be saved for the vehicle
        destination_edge = route[-1]
        routeid = traci.vehicle.getRouteID(vehicle_id)
        typeid = traci.vehicle.getTypeID(vehicle_id)
        pos = traci.vehicle.getPosition(vehicle_id)
        lane = traci.vehicle.getLaneIndex(vehicle_id)
        laneoffset = traci.vehicle.getLanePosition(vehicle_id)
        speed = traci.vehicle.getSpeed(vehicle_id)
        currentVehicleData = {'vehicle_id': vehicle_id, 'routeid': routeid, 'typeid': typeid, 'current_edge': current_edge, 'destination_edge': destination_edge , 'lane':lane,'laneoffset':laneoffset,'speed':speed,'priority': priority}
        AllVehicles.append(currentVehicleData)
        # temporarily removing the vehicle from the network
        traci.vehicle.remove(vehicle_id)
       
    # sort vehicle list based on priority
    sorted_vehicles = sorted(vehicles, key=lambda v: priorities[v], reverse=True)


    # loop over vehicles in sorted order
    for vehicle_id in sorted_vehicles:
        for vehicle_data in AllVehicles:
            if vehicle_data['vehicle_id'] == vehicle_id:
                vehiclerouteid = vehicle_data['routeid']
                vehicletypeid = vehicle_data['typeid']
                currentedge = vehicle_data['current_edge']
                destination = vehicle_data['destination_edge']
                laneind = vehicle_data['lane']
                laneoff = vehicle_data['laneoffset']
                spd = vehicle_data['speed']
                pty = vehicle_data['priority']

                # obtaining info to generate new vehicle id and route
                first_element =vehicle_id.split()[0]
                start_edge_id = currentedge
                destination_edge_id = destination
                if priority < 3:
                    
                    # Random Route Generation
                    network_file_path = "C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/sumotestmap.net.xml"
                    # network_file_path = "C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/Testing Scenarios/sumotesting.net.xml"

                    randomedge = random_next_edge(start_edge_id, network_file_path)
                    if randomedge is not None:#checking if the random edge was generated correctly
                        route = traci.simulation.findRoute(randomedge, destination_edge_id)
                        edge_list =route.edges
                        final_route_edges= [start_edge_id]+list(edge_list)

                 
                    # Adding the vehicle back
                        traci.route.add(str(first_element)+" "+str(step), final_route_edges)
                        traci.vehicle.add(str(first_element)+" "+str(step), str(first_element)+" "+str(step),typeID=vehicletypeid , depart="now",departLane=laneind,departPos=laneoff)
                else:#returning the vehicle to the original path/fastest route
                    Fastestroute = traci.simulation.findRoute(start_edge_id, destination_edge_id)
                    fastedgelist = Fastestroute.edges
                    traci.route.add(str(first_element)+" "+str(step), list(fastedgelist))
                    traci.vehicle.add(str(first_element)+" "+str(step), str(first_element)+" "+str(step),typeID=vehicletypeid , depart="now",departLane=laneind,departPos=laneoff)

# Stop the simulation and close the TraCI connection
traci.close()
sock.close()
print("Disconnected from Unity TCP server")