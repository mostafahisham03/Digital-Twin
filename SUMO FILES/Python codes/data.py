import pandas as pd
import numpy as np

# Load existing dataset
df = pd.read_excel('C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/Dataset.xlsx')

# Set seed for reproducibility
np.random.seed(42)

# Add new features
df['road_inclination'] = np.random.uniform(0, 7, size=len(df))  # Inclination in degrees
df['neighbourhood_density'] = np.random.randint(50, 300, size=len(df))  # Density in people/km²

# Save updated dataset to a new file
df.to_excel('C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/Dataset_with_new_features.xlsx', index=False)

print("✅ Dataset updated and saved successfully.")
