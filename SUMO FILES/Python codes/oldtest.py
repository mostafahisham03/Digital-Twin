import traci
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd

df = pd.read_excel('C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/Dataset.xlsx')

# Preprocessing: split dataset into features and target variable
X = df.drop(['priority'], axis=1) # features (exclude 'priority')
y = df['priority'] # target variable 
X.drop('initial priority', axis=1, inplace=True)
# Creating the Random Forest model with default parameters
rf_model = RandomForestClassifier()

# Training the model on the entire dataset
rf_model.fit(X, y)

# Connect to SUMO and start the simulation
traci.start(['sumo-gui', '-c', 'C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/Testing Scenarios/sumotesting.sumo.cfg'])
step = 0
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    # Get a list of all vehicles currently in the simulation
    vehicles = traci.vehicle.getIDList()
    priorities = {}
    for vehicle_id in vehicles:
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
        # Predict the priority using the Random Forest model
        priority = rf_model.predict([features])[0]
        priorities[vehicle_id] = priority
        print("vehicle id "+str(vehicle_id)+"'s priority is " + str(priority))
        if priority > 3:
            traci.vehicle.setColor(vehicle_id, (255, 0, 0))  # set color to red
        else:
            traci.vehicle.setColor(vehicle_id, (0, 255, 0))  # set color to green




        # Assign the predicted priority to the vehicle
        # traci.vehicle.setPriority(vehicle_id, priority)
    # sort vehicle list based on distance from point
    sorted_vehicles = sorted(vehicles, key=lambda v: priorities[v])

    # reroute vehicles in sorted order
    for vehicle_id in sorted_vehicles:
        traci.vehicle.rerouteTraveltime(vehicle_id)
        print(str(vehicle_id)+"is rerouted at timestep "+str(step))
        
    step += 1
# Stop the simulation and close the TraCI connection
traci.close()