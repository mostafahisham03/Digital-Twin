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
#traci.start(['sumo-gui', '-c', 'C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/sumotest.sumo.cfg'])

step = 0
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    # Get a list of all vehicles currently in the simulation
    vehicles = traci.vehicle.getIDList()
    # routesfile=traci.route.getIDList()
    # print(routesfile)
    priorities = {}
    start_positions ={}
    AllVehicles =[]
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

        # data to be saved for the vehicle
        routeid = traci.vehicle.getRouteID(vehicle_id)
        typeid = traci.vehicle.getTypeID(vehicle_id)
        # route = traci.vehicle.getRoute(vehicle_id)
        pos = traci.vehicle.getPosition(vehicle_id)
        if vehicle_id not in start_positions:
            # add the starting position to the dictionary
            x, y = traci.vehicle.getPosition(vehicle_id)
            start_positions[vehicle_id] = (x, y)
        depart = step
        currentVehicleData = {'vehicle_id': vehicle_id, 'routeid': routeid, 'typeid': typeid, 'pos': pos, 'depart': depart}
        AllVehicles.append(currentVehicleData)
        # print(start_positions)
    # sort vehicle list based on priority
    print("vehicle data array contains :",AllVehicles)
    sorted_vehicles = sorted(vehicles, key=lambda v: priorities[v], reverse=True)
    # loop over vehicles in sorted order
    for vehicle_id in sorted_vehicles:
        # for vehicle_data in AllVehicles:
        #     if vehicle_data['vehicle_id'] == vehicle_id:
        #         vehiclerouteid = vehicle_data['routeid']
        #         vehicletypeid = vehicle_data['typeid']
        #         print(vehicle_id,vehiclerouteid,vehicletypeid)
        #         vehiclepos = vehicle_data['pos']
        #         startingPosition = start_positions[vehicle_id]
        #         vehicledepart = vehicle_data['depart']
                # Adding the vehicle back
                # traci.vehicle.add(vehicle_id,routeID=vehiclerouteid, typeID= vehicletypeid,depart="now",departPos=startingPosition,departSpeed="0")
                # traci.vehicle.changeTarget(vehicle_id, vehicledestination)
        # currentRoute = traci.vehicle.getRouteID(vehicle_id)
        # traci.vehicle.rerouteEffort(vehicle_id)
        # newRoute = traci.vehicle.getRouteID(vehicle_id)
        # Get the route of the vehicle
        route = traci.vehicle.getRoute(vehicle_id)

        # Get the destination (last edge) of the vehicle
        destination = route[-1]
        traci.vehicle.changeTarget(vehicle_id, destination)
        Altroute = traci.vehicle.getRoute(vehicle_id)
        # Print the destination
        print(f"The old route of vehicle {vehicle_id} is {route} and the new route is {Altroute}")
        if(Altroute != route):
            traci.vehicle.setColor(vehicle_id, (255, 100, 255))  # change color
        # traci.vehicle.rerouteEffort(vehID)
        # print(str(vehicle_id)+"is rerouted at timestep "+str(step))
# Stop the simulation and close the TraCI connection
traci.close()
