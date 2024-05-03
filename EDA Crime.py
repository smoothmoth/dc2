import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import folium


# folder_path = "C:/Users/hetvi/Downloads/CombinedFinal"

#Combine CSV's
# df = pd.read_csv("C:/Users/hetvi/Downloads/Combined/metropolitan-outcomes.csv")
# df2 = pd.read_csv("C:/Users/hetvi/Downloads/Combined1/metropolitan-outcomes1.csv")
# df3 = pd.read_csv("C:/Users/hetvi/Downloads/Combined3/metropolitan-outcomes3.csv")
# df4 = pd.read_csv("C:/Users/hetvi/Downloads/Combined2/metropolitan-outcomes2.csv")
# print("all loaded")
# df_con1 = pd.concat([df, df2, df3, df4])
# print("done saving")
# df_con1.to_csv(folder_path + "/metropolitan-outcomes-combined.csv", index=False)

# df1 = pd.read_csv("C:/Users/hetvi/Downloads/Combined/metropolitan-street.csv")
# print(df1['Month'].unique())
# df12 = pd.read_csv("C:/Users/hetvi/Downloads/Combined1/metropolitan-street1.csv")
# print(df12['Month'].unique())
# df13 = pd.read_csv("C:/Users/hetvi/Downloads/Combined3/metropolitan-street3.csv")
# print(df13['Month'].unique())
# df14 = pd.read_csv("C:/Users/hetvi/Downloads/Combined2/metropolitan-street2.csv")
# print(df14['Month'].unique())
# print("all loaded")
# df_con2 = pd.concat([df1, df12, df13, df14])
# print(df_con2['Month'].unique())
# print("done saving")
#
# df_con2.to_csv(folder_path + "/metropolitan-street-combined.csv", index=False)
#
# df02 = pd.read_csv("C:/Users/hetvi/Downloads/Combined/metropolitan-stop-and-search.csv")
# df22 = pd.read_csv("C:/Users/hetvi/Downloads/Combined1/metropolitan-stop-and-search1.csv")
# df23 = pd.read_csv("C:/Users/hetvi/Downloads/Combined3/metropolitan-stop-and-search3.csv")
# print("all loaded")
# df_con3 = pd.concat([df02, df22, df23])
# print("done saving")
#
# df_con3.to_csv(folder_path + "/metropolitan-stop-and-search-combined.csv", index=False)

######################################### EDA  Outcomes ###############################################

df = pd.read_csv("CombinedFinal/metropolitan-outcomes-combined.csv")
# Initial Exploration
# df.info()
# df = df.dropna()
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
plt.xlabel("Month")
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

# m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=10)
# for index, row in df.iterrows():
#     folium.Marker([row['Latitude'], row['Longitude']], popup=f"Crime ID: {row['Crime ID']}").add_to(m)
#
# m.save('crime_map.html')
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

####################################### EDA Street ####################################################

df2 = pd.read_csv("CombinedFinal/metropolitan-street-combined.csv")
## Inital exploration of data types
# df2.info()
# print(df2.describe())
#
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

# Types of crime count
sns.countplot(data=df2, x='Crime type')
plt.title("Types of crime count")
plt.xticks(rotation=45, ha='right')
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
plt.legend.remove()