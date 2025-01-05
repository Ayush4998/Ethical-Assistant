import numpy as np
from sklearn.tree import DecisionTreeClassifier
import joblib
import os

# Training data (features: [impact, net_utility], labels: 1 = Ethical, 0 = Unethical)
train_data = [
    ([8, 7], 1),  # High impact, high net utility => Ethical
    ([6, 3], 1),  # Medium impact, positive net utility => Ethical
    ([9, -2], 0),  # High impact, negative net utility => Unethical
    ([2, 8], 1),  # Low impact, high net utility => Ethical
    ([4, -5], 0),  # Medium impact, negative net utility => Unethical
    ([10, -10], 0),  # Extreme impact, extremely negative net utility => Unethical
    ([5, 6], 1)   # Medium impact, positive net utility => Ethical
]

# Split the data into features and labels
X_train = np.array([x for x, y in train_data])
y_train = np.array([y for x, y in train_data])

# Initialize the decision tree model
decision_tree = DecisionTreeClassifier()

# Train the model
decision_tree.fit(X_train, y_train)

# Save the trained decision tree model
model_dir = "trained_models"
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

joblib.dump(decision_tree, os.path.join(model_dir, "decision_tree_model.pkl"))
print(f"Decision tree model saved to {os.path.join(model_dir, 'decision_tree_model.pkl')}")

# Example usage: predict if a new scenario is ethical or not
# Test data (replace with actual extracted values)
test_data = np.array([[7, 5]])  # Example: high impact, positive net utility
prediction = decision_tree.predict(test_data)
print(f"Prediction: {'Ethical' if prediction == 1 else 'Unethical'}")

if __name__ == "__main__":
    pass
