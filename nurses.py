# -*- coding: utf-8 -*-


import os
os.chdir('./data')

import pandas as pd
nurses_data = pd.read_excel("Nurses.xlsx")
nurses_data.head()

#Replace 'na' values with NaN in the "Description" column
nurses_data['Description'].replace('na', pd.NA, inplace=True)
#Re-check for missing values
missing_values_updated = nurses_data.isnull().sum()
missing_values_updated

# Impute missing values in the "Description" column
nurses_data['Description'].fillna("No description provided", inplace=True)
# Check the data types of the columns
column_data_types = nurses_data.dtypes
column_data_types

#Convert Start time and End time to datetime format for calculation
nurses_data['Start datetime'] = pd.to_datetime(nurses_data['Start time'].astype(str))
nurses_data['End datetime'] = pd.to_datetime(nurses_data['End time'].astype(str))
#Calculate duration
nurses_data['calculated_duration'] = (nurses_data['End datetime'] - nurses_data['Start datetime']).dt.total_seconds() / 3600
#Drop temporary datetime columns
nurses_data.drop(['Start datetime', 'End datetime'], axis=1, inplace=True)
#Display the calculated duration along with the original duration for comparison
nurses_data[['duration', 'calculated_duration']].head()

#Defining potential binary columns
binary_columns = [
    'Stress level', 'COVID related', 'Treating a covid patient', 'Patient in Crisis',
    'Patient or patient\'s family', 'Doctors or colleagues',
    'Administration, lab, pharmacy, radiology, or other ancilliary services\n',
    'Increased Workload', 'Technology related stress', 'Lack of supplies', 'Documentation',
    'Competency related stress', 'Saftey (physical or physiological threats)',
    'Work Environment - Physical or others: work processes or procedures'
]
#Inspecting unique values of these columns
binary_columns_unique_values = {col: nurses_data[col].unique() for col in binary_columns}
binary_columns_unique_values

# Convert 'na' values to NaN for the potential binary columns
for col in binary_columns:
    nurses_data[col].replace('na', pd.NA, inplace=True)
# Check the number of missing values in these columns
missing_values_binary_columns = nurses_data[binary_columns].isnull().sum()
missing_values_binary_columns

from sklearn.model_selection import train_test_split
#Splitting the data into training and testing subsets
train_data, test_data = train_test_split(nurses_data, test_size=0.25, random_state=42)
#Impute missing values in the training set using mode
for col in binary_columns:
    mode_value = train_data[col].mode()[0]
    train_data[col].fillna(mode_value, inplace=True)
#Check if there are any missing values left in the training data
missing_values_train = train_data[binary_columns].isnull().sum()
missing_values_train

import matplotlib.pyplot as plt
import seaborn as sns
#Set up the figure and axes for the grid of plots
fig, axes = plt.subplots(nrows=7, ncols=2, figsize=(18, 30))
#Iterate through binary columns and axes to plot side by side
for col, ax in zip(binary_columns, axes.flatten()):
    sns.boxplot(x=train_data[col], y=train_data['Stress level'].astype(float), ax=ax)
    ax.set_title(f"Distribution of Stress Level by {col}")
    ax.set_xlabel(col)
    ax.set_ylabel('Stress Level')
#Adjust layout
plt.tight_layout()
plt.show()

#Feature Selection and Model Training
#Define the features and target for training data
X_train = train_data[binary_columns].astype(float)
y_train = train_data['Stress level'].astype(float)
#Cross-validation for model selection
#Initializing models
models = {
    'SVR': SVR(),
    'Linear Regression': LinearRegression(),
    'Decision Tree Regression': DecisionTreeRegressor()
}
#Cross-validate models and store results
cv_rmse_results = {}
for name, model in models.items():
    cv_rmse = -np.mean(cross_val_score(model, X_train, y_train, cv=5, scoring=rmse_scorer))
    cv_rmse_results[name] = cv_rmse
#Train the most promising model (SVR) on the entire training data
svr_model = SVR()
svr_model.fit(X_train, y_train)
#Prepare the test data
#Impute missing values in the test set using mode values from training set
for col in binary_columns:
    mode_value = train_data[col].mode()[0]
    test_data[col].fillna(mode_value, inplace=True)
X_test = test_data[binary_columns].astype(float)
y_test = test_data['Stress level'].astype(float)
#Evaluate the SVR model on the test data
y_pred = svr_model.predict(X_test)
test_rmse = compute_rmse(y_test, y_pred)
cv_rmse_results, test_rmse
