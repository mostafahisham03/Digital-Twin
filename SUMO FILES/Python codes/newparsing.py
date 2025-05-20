import xml.etree.ElementTree as ET
import pandas as pd

# parse the XML file
tree = ET.parse('C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/results.xml')
root = tree.getroot()

# create a list of dictionaries to store the data for each vehicle
vehicles_data = []

# loop through all the <timestep> elements
for timestep in root.findall('.//timestep'):
    # get the timestep number
    timestep_number = timestep.get('time')

    # check if the timestep number exceeds 100
    if float(timestep_number) > 100.0:
        break

    # loop through all the <vehicle> elements within the current timestep
    for vehicle in timestep.findall('.//vehicle'):
        vehicle_data = {
            'timestep': timestep_number,
            'id': vehicle.get('id'),
            'eclass': vehicle.get('eclass'),
            'CO2': vehicle.get('CO2'),
            'CO': vehicle.get('CO'),
            'HC': vehicle.get('HC'),
            'NOx': vehicle.get('NOx'),
            'PMx': vehicle.get('PMx'),
            'fuel': vehicle.get('fuel'),
            'electricity': vehicle.get('electricity'),
            'noise': vehicle.get('noise'),
            'route': vehicle.get('route'),
            'type': vehicle.get('type'),
            'waiting': vehicle.get('waiting'),
            'lane': vehicle.get('lane'),
            'pos': vehicle.get('pos'),
            'speed': vehicle.get('speed'),
            'angle': vehicle.get('angle'),
            'x': vehicle.get('x'),
            'y': vehicle.get('y')
        }
        vehicles_data.append(vehicle_data)

# create a DataFrame from the list of dictionaries
df = pd.DataFrame(vehicles_data)
print(df)
print(df.columns)
# save the DataFrame to a CSV file
df.to_csv('filename.csv', index=False)
