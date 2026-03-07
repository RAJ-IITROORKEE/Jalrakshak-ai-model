import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from utils.preprocess import load_data

# Load dataset — absolute path so the script works from any working directory
_data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'water_potability.csv')
df = load_data(_data_path)

X = df[['ph','tds','conductivity','turbidity']]
y = df['potability']

# Train test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=200)

model.fit(X_train, y_train)

# Save model — absolute path so the script works from any working directory
_output_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'water_model.pkl')
joblib.dump(model, _output_path)

print("Model trained and saved successfully")