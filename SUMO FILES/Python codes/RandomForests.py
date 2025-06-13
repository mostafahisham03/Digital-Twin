from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    max_error,
    accuracy_score
)
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load dataset
df = pd.read_excel('C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/Dataset.xlsx')

# Preprocessing: split dataset into features and target variable
X = df.drop(['initial priority', 'priority'], axis=1)
y = df['priority']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model training
rf_model = RandomForestRegressor()
rf_model.fit(X_train, y_train)

# Prediction
y_pred = rf_model.predict(X_test)

# --- Metrics ---
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
max_err = max_error(y_test, y_pred)

# Classification-style Accuracy (only valid if priority is integer-valued)
y_pred_class = np.round(y_pred)
accuracy = accuracy_score(y_test, y_pred_class)

# Print metrics
print("📊 Random Forest Performance Metrics:")
print(f"Mean Squared Error (MSE): {mse:.6f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.6f}")
print(f"Mean Absolute Error (MAE): {mae:.6f}")
print(f"R² Score: {r2:.6f}")
print(f"Maximum Error: {max_err:.6f}")
print(f"Classification-style Accuracy (Rounded): {accuracy:.6f}")

# --- Visualization ---
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, alpha=0.6, edgecolors='k')
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2, label='Ideal Prediction Line')
plt.xlabel('Actual Priority')
plt.ylabel('Predicted Priority')
plt.title('Random Forest: Actual vs Predicted Priorities')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Residual plot
residuals = y_test - y_pred
plt.figure(figsize=(8, 6))
plt.scatter(y_pred, residuals, alpha=0.6, edgecolors='k')
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted Priority')
plt.ylabel('Residuals')
plt.title('Random Forest: Residual Plot')
plt.grid(True)
plt.tight_layout()
plt.show()