import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import folium
import re
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

######################################### EDA  Outcomes ###############################################

df = pd.read_csv("D:\DC2_Output\metropolitan-outcomes.csv") # Insert the path to the outcomes file that you get after Powershell step 1 in the README
# Initial Exploration
# df.info()
# print(df.count())
df = df.dropna()
df['Month'] = pd.to_datetime(df['Month'], format='%Y-%m')

# Create a new column 'Year' from the 'Month' column
df['Year'] = df['Month'].dt.year
# print(df['Month'].unique())
# print(df['Reported by'].unique())
# print(df['Falls within'].unique())
# print(df['LSOA code'].unique())
# print(df['Location'].unique())
# print(len(df['LSOA code'].unique()))
# print(df['LSOA name'].unique())
# print(df['Outcome type'].unique())
# print(df['Outcome type'].value_counts())
# print(df.describe())
# print(df['Crime ID'].value_counts())
# print(df[df['Crime ID']=='8e4e2c642355be75d0619beddd7c17df12a6003f8d35ba1555e10217fbae86d0']['Outcome type'])

# Histograms for Longitude and Latitude
plt.hist(x=df['Longitude'], bins=100)
plt.xlabel("Longitude")
plt.title("Longitude histogram")
plt.show()

plt.hist(x=df['Latitude'], bins=100)
plt.xlabel("Latitude")
plt.title("Latitude histogram")
plt.show()

# Number of crimes over time
df['Month'] = pd.to_datetime(df['Month'])
df['Month'].value_counts().sort_index().plot(kind='line', figsize=(10, 6))
plt.title("Number of Crimes Over Time")
plt.xlabel("Year")
plt.ylabel("Number of Crimes")
plt.show()

# Count of Outcome Types by Month'
outcome_counts = df.groupby(['Month', 'Outcome type']).size().reset_index(name='count')

outcome_counts_pivot = outcome_counts.pivot(index='Month', columns='Outcome type', values='count').fillna(0)

outcome_counts_pivot.plot(kind='bar', stacked=True, figsize=(10, 6))
plt.title('Count of Outcome Types by Month')
plt.xlabel('Month')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.legend(title='Outcome Type')
plt.show()


# Counts of Different Outcomes for Each Year
per_year = df.groupby(['Year', 'Outcome type']).size().reset_index(name='count')

for year in per_year['Year'].unique():
    # Plot grouped bar chart
    print(per_year[per_year['Year'] == year])
    sns.barplot(data=per_year[per_year['Year']==year], x='Year', y='count', hue='Outcome type', palette='viridis')
    plt.title('Counts of Different Outcomes for Each Year')
    plt.xlabel('Year')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.title('Counts of Different Outcomes for Each Year')

# Plot line graph for each outcome type over the years
outcome_counts2 = df.groupby(['Year', 'Outcome type']).size().unstack(fill_value=0)
print(outcome_counts2)
plt.figure(figsize=(12, 8))
for outcome_type in outcome_counts2.columns:
    plt.plot(outcome_counts2.index, outcome_counts2[outcome_type], label=outcome_type)

plt.title('Counts of Different Outcome Types Over the Years')
plt.xlabel('Year')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.legend(title='Outcome Type')
plt.tight_layout()
plt.show()

# Plotting longitude and latitude
plt.figure(figsize=(10, 6))
plt.scatter(df['Longitude'], df['Latitude'], c='red', marker='o')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Crime Data Plot')
plt.grid(True)
plt.show()

m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=10)
# for index, row in df.iterrows():
#     folium.Marker([row['Latitude'], row['Longitude']], popup=f"Crime ID: {row['Crime ID']}").add_to(m)
#
m.save('crime_map.html')
# m


# Count crime occurrences of each location
location_counts = df['Location'].value_counts().reset_index().rename(columns={'Location': 'Location', 'count': 'Counts'})
# print(location_counts)
# print(location_counts.describe())
counts_sorted = location_counts.sort_values(by='Counts', ascending=False)
# print(counts_sorted[0:20])


# Plot bar chart for number of crimes per location
plt.figure(figsize=(10, 6))
sns.barplot(data=counts_sorted[0:20], x='Location', y='Counts'  )
plt.xlabel('Location')
plt.ylabel('Number of Crimes')
plt.title('Number of Crimes per Location')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# Crime in each LSOA
lsoa_counts = df['LSOA name'].value_counts().reset_index().rename(columns={'LSOA name': 'LSOA name', 'count': 'Counts'})
print(lsoa_counts)
print(lsoa_counts .describe())
counts_lsoa = lsoa_counts .sort_values(by='Counts', ascending=False)
sns.barplot(data=counts_lsoa[0:20], x='LSOA name', y='Counts')
plt.title("Crimes in each LSOA")
plt.xticks(rotation=45, ha='right')
plt.show()

# ####################################### EDA Street ####################################################

df2 = pd.read_csv("D:\DC2_Output\metropolitan-street-combined.csv")  # Insert the path to the streets file that you get after Powershell step 1 in the README
## Inital exploration of data types
# df2.info()
# print(df2.count())
# df3 = df2.drop_duplicates(subset=None, keep='first', inplace=False)
# print(df3.count())
# print(df2.describe())
# print(df2['Month'].unique())
# print(df2['Reported by'].unique())
# print(df2['Falls within'].unique())
# print(df2['LSOA code'].unique())
# print(df2['Location'].unique())
# print(len(df2['LSOA code'].unique()))
# print(df2['LSOA name'].unique())
# print(df2['Crime type'].unique())
# print(df2['Crime type'].value_counts())
# print(df2['Crime ID'].value_counts())
# print(df2['Last outcome category'].unique())
# print(df2['Last outcome category'].value_counts())
# print(df2['Context'].unique())
# print(df2[df2['Crime ID']== '490b595dc6eb4b0a3e1f8d7fa53d2be5460d146d8f133a8ee20ed3c3b7319bc3']['Last outcome category'].unique())
# print(df.info())
df2['Month'] = pd.to_datetime(df2['Month'], format='%Y-%m')

# Create a new column 'Year' from the 'Month' column
df2['Year'] = df2['Month'].dt.year




# Types of crime count
sns.countplot(data=df2, x='Crime type')
plt.title("Types of crime count")
plt.xticks(rotation=45, ha='right')
plt.show()
plt.savefig('alldata.png')

dfn = df2[df2['Year'] <= 2019]

# Display the filtered DataFrame to ensure it has the correct rows
print(dfn['Year'].unique())

plt.figure(figsize=(10, 6))
sns.countplot(data=dfn, x='Crime type')
plt.title("Types of Crime Count Pre-COVID")
plt.xticks(rotation=45, ha='right')
plt.savefig('non-coviddata.png')
plt.show()

# Last outcome categories count
sns.countplot(data=df2, x='Last outcome category')
plt.title("Last outcome categories")
plt.xticks(rotation=45, ha='right')
plt.show()


# Crimes in each lsoa counts
lsoa_counts2 = df2['LSOA name'].value_counts().reset_index().rename(columns={'LSOA name': 'LSOA name', 'count': 'Counts'})
# print(lsoa_counts2)
# print(lsoa_counts2.describe())
counts_lsoa2 = lsoa_counts2 .sort_values(by='Counts', ascending=False)
sns.barplot(data=counts_lsoa2[0:20], x='LSOA name', y='Counts')
plt.title("Crimes in each LSOA")
plt.xticks(rotation=45, ha='right')
plt.show()

# Crime count by month
crime_count = df2.groupby(['Month', 'Crime type']).size().reset_index(name='count')
print(crime_count)
crime_count_pivot = crime_count.pivot(index='Month', columns='Crime type', values='count').fillna(0)

crime_count_pivot.plot(kind='bar', stacked=True, figsize=(10, 6))
plt.title('Count of Crime Types by Month')
plt.xlabel('Month')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.legend(title='Crime Type')
plt.show()


crime_count = df2.groupby(['Month', 'Crime type']).size().reset_index(name='count')
print(crime_count)
crime_count_pivot = crime_count.pivot(index='Month', columns='Crime type', values='count').fillna(0)
print(len(df2['Location'].unique()))
print(df2['Location'].unique()[150:250])


print(df2['Month'].unique())

print(df2[df2['Month'] == '2018-02'])
# Define categories and their associated regex patterns
categories = {
    "Transportation": re.compile(r"\b(subway|train|railway station|bus|airport|nderground|tube|metro|tram|petrol station|drive|parking|highway)\b", re.IGNORECASE),
    "Markets/Malls": re.compile(r"\b(shopping|mall|market|plaza|bazaar|close|supermarket|square)\b", re.IGNORECASE),
    "Parks/Recreation": re.compile(r"\b(park|garden|beach|trail|grove|sports|recreation|cinema|concert|gardens|terrace|walk|fields|hill|lodge|lawn|cottages|vineyard|path)\b", re.IGNORECASE),
    "Restaurants/Cafes": re.compile(r"\b(restaurant|cafe|diner|bistro|nightclub)\b", re.IGNORECASE),
    "Streets": re.compile(r"\b(road|avenue|lane|street|place|way|row|alley|bridge|route)\b", re.IGNORECASE),
    "Education": re.compile(r"\b(school|college|university|preschool|educational)\b", re.IGNORECASE),
    "Buildings": re.compile(r"\b(court|police station|Conference|Exhibition Centre|hospital|bank|broadway)\b", re.IGNORECASE),
}

# Function to classify locations
def classify_location(location, categories):
    for category, pattern in categories.items():
        if pattern.search(location):
            return category
    return "Other"

crime_type = df2['Crime type'].unique()
for type in crime_type:
    # Read locations from a file (e.g., CSV)
    new = df2[df2['Crime type']== type]
    locations = new['Location'].tolist()

    # Classify each location
    classified_locations = defaultdict(int)

    for location in locations:
        category = classify_location(location, categories)
        classified_locations[category] += 1
        # if category == 'Other':
        #     print(location)

    # Convert classified locations to a DataFrame for plotting
    classified_df = pd.DataFrame.from_dict(classified_locations, orient='index', columns=['count'])
    classified_df = classified_df.reset_index().rename(columns={'index': 'category'})

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(classified_df['category'], classified_df['count'], color='skyblue')
    plt.xlabel('Category')
    plt.ylabel('Number of Locations')
    plt.title(f'Number of Locations per Category per crime {type}')
    plt.xticks(rotation=45)
    plt.show()

