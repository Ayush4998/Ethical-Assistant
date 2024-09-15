import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

# Example dataset (You should replace this with your actual dataset)
# For this example, I'll create a dummy dataset.
# Replace this with actual features and labels
data = {
    'outcome_harm': [0.1, 0.4, 0.3, 0.9, 0.2, 0.7],   # Harm percentage (Dummy values)
    'outcome_benefit': [0.8, 0.5, 0.6, 0.2, 0.7, 0.1], # Benefit percentage (Dummy values)
    'num_stakeholders': [3, 5, 2, 4, 6, 3],            # Number of stakeholders affected
    'ethical': [1, 1, 1, 0, 1, 0]                      # 1 for ethical, 0 for not ethical
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Define features (X) and labels (y)
X = df[['outcome_harm', 'outcome_benefit', 'num_stakeholders']]
y = df['ethical']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the Decision Tree Classifier
clf = DecisionTreeClassifier()

# Train the model
clf.fit(X_train, y_train)

# Predict on the test set
y_pred = clf.predict(X_test)

# Calculate the accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Save the trained model
model_path = os.path.join("trained_models\decision_tree_model", "decision_tree_model.pkl")

# Ensure the directory exists
if not os.path.exists("trained_models"):
    os.makedirs("trained_models")

joblib.dump(clf, model_path)
print(f"Decision tree model saved to {model_path}")

