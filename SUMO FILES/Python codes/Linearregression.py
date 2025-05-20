import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error

# Load the dataset
df = pd.read_excel('C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/Dataset.xlsx')

# Preprocessing: split dataset into features and target variable
X = df.drop(['initial priority', 'priority'], axis=1) # features (exclude 'priority')
y = df['priority'] # target variable 

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the linear regression model
lr = LinearRegression()

# Train the model on the training data
lr.fit(X_train, y_train)

# Make predictions on the testing data
y_pred = lr.predict(X_test)

# Evaluate the accuracy of the model
r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = mse**(0.5)
print('R^2 score:', r2)
print('Mean squared error:', mse)
print('Root mean squared error:', rmse)
import matplotlib.pyplot as plt

# Scatter plot: Actual vs. Predicted Values
plt.scatter(y_test, y_pred)
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title('Linear Regression: Actual vs. Predicted Values')
plt.show()

# Residual plot
residuals = y_test - y_pred
plt.scatter(y_pred, residuals)
plt.xlabel('Predicted Values')
plt.ylabel('Residuals')
plt.title('Linear Regression: Residual Plot')
plt.axhline(y=0, color='r', linestyle='--')  # Add a horizontal line at y=0 for reference
plt.show()

