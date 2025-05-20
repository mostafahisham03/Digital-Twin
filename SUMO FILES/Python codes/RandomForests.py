from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel('C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/Dataset.xlsx')

# Preprocessing: split dataset into features and target variable
X = df.drop(['initial priority', 'priority'], axis=1) # features (exclude 'priority')
y = df['priority'] # target variable 
# Splitting the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Creating the Random Forest model with default parameters
rf_model = RandomForestRegressor()

# Training the model on the train set
rf_model.fit(X_train, y_train)

# Predicting the labels for test set
y_pred = rf_model.predict(X_test)

# Calculating the mean squared error
mse = mean_squared_error(y_test, y_pred)

# Plotting the actual vs predicted values
plt.scatter(y_test, y_pred)
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title('Random Forest:Actual vs Predicted Values')
plt.show()

print("Mean squared error:", mse)
