import pandas as pd
import re

df2 = pd.read_csv("CombinedFinal/metropolitan-street-combined.csv")

# # Initial Cleaning
df2 = df2.drop_duplicates()
df2['Month'] = pd.to_datetime(df2['Month']).dt.date
# print(df2['Month'].unique())
# print(df2)
df2 = df2.dropna(subset=['Crime ID'])
# print(df2)
# print(df2.info())
df2 = df2.drop(columns=['Context', 'Reported by', 'Falls within'])
# Convert all columns to type string except latitude and longitude
for col in df2.columns:
    if col not in ['latitude', 'longitude', 'Month']:
        df2[col] = df2[col].astype(str)

## Boroughs for each LSOA
pattern = r'^[^\d]+'

# Function to extract the name using regex
def extract_name(text):
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    else:
        return "No match found."

# Apply the function to the DataFrame column
df2['Borough'] = df2['LSOA name'].apply(extract_name)

# Aggregating data per LSOA per month per year
one_hot_encoded = pd.get_dummies(df2['Crime type'])
one_hot_encoded = one_hot_encoded.astype(int)
two_hot_encoded = pd.get_dummies(df2['Last outcome category'])
two_hot_encoded = two_hot_encoded.astype(int)

df_final = pd.concat([df2, one_hot_encoded, two_hot_encoded], axis=1)
print(df_final.columns)
df_new = df_final.drop(columns=['Longitude', 'Latitude', 'Location', 'LSOA code', 'Crime type', 'Last outcome category'])
df_aggregate = df_new.groupby(['LSOA name', 'Month']).sum().reset_index()
print(df_aggregate)