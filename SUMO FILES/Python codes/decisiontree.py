import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    mean_squared_error,
    mean_absolute_error,
    max_error,
    r2_score
)
import matplotlib.pyplot as plt
import numpy as np

# Load the dataset
df = pd.read_excel('C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/Dataset.xlsx')

# Preprocessing
X = df.drop(['initial priority', 'priority'], axis=1)
y = df['priority']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define and train the Decision Tree classifier
dtc = DecisionTreeClassifier(max_depth=6)
dtc.fit(X_train, y_train)

# Make predictions
y_pred = dtc.predict(X_test)

# --- Metrics ---
accuracy = accuracy_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred)
max_err = max_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
residuals = y_test - y_pred

# Print metrics
print("📊 Decision Tree Classifier Metrics:")
print(f"Accuracy: {accuracy:.6f}")
print(f"R² Score: {r2:.6f}")
print(f"Mean Squared Error (MSE): {mse:.6f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.6f}")
print(f"Mean Absolute Error (MAE): {mae:.6f}")
print(f"Maximum Error: {max_err}")

# --- Visualization 1: Actual vs. Predicted ---
plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, alpha=0.6, edgecolors='k', label='Predictions')

min_val = min(y_test.min(), y_pred.min())
max_val = max(y_test.max(), y_pred.max())

plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Ideal Prediction Line', zorder=10)

plt.xlim(min_val, max_val)
plt.ylim(min_val, max_val)

plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title('Decision Tree: Actual vs Predicted')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


# --- Visualization 2: Residual Plot ---
# Residual plot
residuals = y_test - y_pred
plt.figure(figsize=(8, 6))
plt.scatter(y_pred, residuals, alpha=0.6, edgecolors='k')
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted Priority')
plt.ylabel('Residuals')
plt.title('Decision Tree: Residual Plot')
plt.grid(True)
plt.tight_layout()
plt.show()