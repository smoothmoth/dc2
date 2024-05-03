import pandas as pd

def highest_proportion(chosen_measure, start_year, end_year):
    df = pd.read_excel('DC2_data/PAS_T&Cdashboard_to Q3 23-24.xlsx', sheet_name='Borough')

    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

    filtered_df = df[(df['Measure'] == chosen_measure) &
                     (df['Date'].dt.year >= start_year) &
                     (df['Date'].dt.year <= end_year)]

    avg_proportion_by_borough = filtered_df.groupby('Borough')['Proportion'].mean()

    highest_avg_borough = avg_proportion_by_borough.idxmax()
    highest_avg_value = avg_proportion_by_borough.max()

    return highest_avg_borough, highest_avg_value

chosen_measure = "\"Good Job\" local"
start_year = 2020
end_year = 2023

def lowest_proportion(chosen_measure, start_year, end_year):
    df = pd.read_excel('DC2_data/PAS_T&Cdashboard_to Q3 23-24.xlsx', sheet_name='Borough')

    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

    filtered_df = df[(df['Measure'] == chosen_measure) &
                     (df['Date'].dt.year >= start_year) &
                     (df['Date'].dt.year <= end_year)]

    avg_proportion_by_borough = filtered_df.groupby('Borough')['Proportion'].mean()

    highest_avg_borough = avg_proportion_by_borough.idxmin()
    highest_avg_value = avg_proportion_by_borough.min()

    return highest_avg_borough, highest_avg_value

print(highest_proportion(chosen_measure, start_year, end_year))