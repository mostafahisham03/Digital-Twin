import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load the dataset
df = pd.read_excel('C:/Users/tefah/OneDrive/Desktop/Digital Twin/SUMO FILES/Dataset.xlsx')

# Preprocessing: split dataset into features and target variable
X = df.drop(['initial priority', 'priority'], axis=1) # features (exclude 'initial priority')
y = df['priority'] # target variable 

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the decision tree model with max depth of 5
dtc = DecisionTreeClassifier(max_depth=6)

# Train the model on the training data
dtc.fit(X_train, y_train)

# Make predictions on the testing data
y_pred = dtc.predict(X_test)

# Evaluate the accuracy of the model
accuracy = accuracy_score(y_test, y_pred)

# Calculate the maximum percentage error in the prediction
max_error = max(abs(y_test - y_pred))

print('Accuracy:', accuracy)
print('Maximum error:', max_error)
import matplotlib.pyplot as plt

# Scatter plot: Actual vs. Predicted Values
plt.scatter(y_test, y_pred)
plt.xlabel('Actual Values')
plt.ylabel('Predicted Values')
plt.title('Decision Tree: Actual vs. Predicted Values')
plt.show()
