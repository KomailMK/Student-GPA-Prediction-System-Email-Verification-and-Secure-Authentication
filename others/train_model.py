import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
# from sklearn.model_selection import cross_val_score 
import joblib

# Load the dataset
data = pd.read_csv('student_performance_data.csv')

# Define feature columns and target column
features = ['attendance', 'study_hours', 'past_cgpa', 'quiz_performance', 'class_participation']
target = 'final_gpa'

# Check for missing values in the target column
# missing_targets = data['final_gpa'].isna().sum()
# # missing_targets2 = data['attendance'].isna().sum()
# print(f"Number of missing values in the target column (final_gpa): {missing_targets}")
# print(f"Number of missing values in the target column (attendance): {missing_targets2}")
# Drop rows where target is missing
print("Number of missing values in the target column (final_gpa):", data['final_gpa'].isna().sum())
#to handle missing values
data['final_gpa'] = data['final_gpa'].fillna(data['final_gpa'].mean())
data['attendance'] = data['attendance'].fillna(data['attendance'].mean())
data['study_hours'] = data['study_hours'].fillna(data['study_hours'].mean())
data['past_cgpa'] = data['past_cgpa'].fillna(data['past_cgpa'].mean())
data['quiz_performance'] = data['quiz_performance'].fillna(data['quiz_performance'].mean())
data['class_participation'] = data['class_participation'].fillna(data['class_participation'].mean())

print("Number of missing values in the target column (final_gpa):", data['final_gpa'].isna().sum())

# Re-define features and target after handling missing values
X = data[features]
y = data[target]

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define a pipeline for preprocessing and modeling
pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='mean')),  # Handle missing values in features
    ('scaler', MinMaxScaler()),  # Scale features to 0–1 range
    ('model', RandomForestRegressor(random_state=42))  # Model
])


# Train the model
model = pipeline.fit(X_train, y_train)
x_train_pred = model.predict(X_train)

# Evaluate the model

accuracy = r2_score(y_train, x_train_pred)
print("Accuracy Score of Model:", round(accuracy * 100, 2))



# Save the trained model
joblib.dump(pipeline, 'final_gpa_model.pkl')

print("\nModel training completed and saved as 'final_gpa_model.pkl'")
