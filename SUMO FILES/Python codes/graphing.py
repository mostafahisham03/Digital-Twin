import matplotlib.pyplot as plt

# Root Mean Square Errors
rmse_lr = 1.5
rmse_nn = 20
rmse_dt = 2
rmse_rf = 2.5

# Model names
models = ['LinearReg', 'NeuralNet', 'DecTrees', 'RandForest']

# RMSE values
rmse_values = [rmse_lr, rmse_nn, rmse_dt, rmse_rf]

# Plotting the bar graph
plt.bar(models, rmse_values)
plt.xlabel('Models')
plt.ylabel('Training Time (minutes)')
plt.title('Comparison of Training Time for Different Models')
plt.xticks(rotation=45)
plt.show()
