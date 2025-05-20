import xml.etree.ElementTree as ET
import pandas as pd

# parse the XML file
tree = ET.parse('C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/results.xml')
root = tree.getroot()

# create a list of dictionaries to store the data for each vehicle
vehicles_data = []

# loop through all the <vehicle> elements and extract their data
for vehicle in root.findall('.//vehicle'):
    vehicle_data = {
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
# save the DataFrame to an Excel file
df.to_csv('filename.csv', index=False)
