import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np


def process_csv(input_file, area):
    df = pd.read_csv(input_file)

    df = df[[area, 'Q60', 'Q61', 'Q62A', 'Q62C', 'Q62F', 'Q62TG', 'NQ135BH', 'Q131', 'Q133', 'MONTH']]

    if area not in df.columns:
        raise KeyError(f"'{area}' column not found in the DataFrame")

    value_mapping_1 = {
        'Strongly agree': 1,
        'Tend to agree': 0.75,
        'Neither agree nor disagree': 0.5,
        'Tend to disagree': 0.25,
        'Strongly disagree': 0,
        'NA': 'NA'
    }

    value_mapping_2 = {
        'Excellent': 1,
        'Good': 0.75,
        'Fair': 0.5,
        'Poor': 0.25,
        'Very poor': 0,
        'NA': 'NA'
    }

    value_mapping_3 = {
        'Very well informed': 1,
        'Fairly well informed': 0.5,
        'Not at all informed': 0,
        'NA': 'NA'
    }

    df['Q60'] = df['Q60'].map(value_mapping_2)
    df['Q61'] = df['Q61'].map(value_mapping_2)
    df['Q62A'] = df['Q62A'].map(value_mapping_1)
    df['Q62C'] = df['Q62C'].map(value_mapping_1)
    df['Q62F'] = df['Q62F'].map(value_mapping_1)
    df['Q62TG'] = df['Q62TG'].map(value_mapping_1)
    df['NQ135BH'] = df['NQ135BH'].map(value_mapping_1)
    df['Q131'] = df['Q131'].map(value_mapping_3)
    df['Q133'] = df['Q133'].map(value_mapping_3)

    # Clean area column
    df[area] = df[area].str.strip()
    df = df[df[area] != 'N/A']
    df = df.dropna(subset=[area])

    # Replace empty strings with NaN
    df.replace("", np.nan, inplace=True)

    # Drop rows where any of the relevant columns have NaN
    df.dropna(subset=['Q60', 'Q61', 'Q62A', 'Q62C', 'Q62F', 'Q62TG', 'NQ135BH', 'Q131', 'Q133'], inplace=True)

    weights = {
        'Q60': 0.2,
        'Q62C': 0.2,
        'Q61': 0.1,
        'Q62A': 0.1,
        'Q62F': 0.1,
        'Q62TG': 0.1,
        'NQ135BH': 0.1,
        'Q131': 0.05,
        'Q133': 0.05
    }

    def calculate_confidence(row):
        total_weight = 0
        weighted_sum = 0
        for column, weight in weights.items():
            if pd.notnull(row[column]):
                weighted_sum += row[column] * weight
                total_weight += weight
        if total_weight == 0:
            return np.nan
        return weighted_sum / total_weight

    df['Confidence'] = df.apply(calculate_confidence, axis=1)

    df['Month_Year'] = df['MONTH'].str.extract(r'(\d{2}) \((\w+ \d{4})\)', expand=True)[1]
    df['Month_Year'] = pd.to_datetime(df['Month_Year'], format='%b %Y')

    return df[[area, 'Confidence', 'Month_Year']]


def calculate_average_confidence(df, area):
    df['Confidence'] = pd.to_numeric(df['Confidence'], errors='coerce')

    avg_confidence = df.groupby(area)['Confidence'].mean().reset_index()
    avg_confidence = avg_confidence.sort_values(by='Confidence')

    return avg_confidence


def average_confidence_over_time(files, start_month, start_year, end_month, end_year, area):
    avg_mps_list = []
    start_date = pd.to_datetime(f'{start_year}-{start_month}-01', format='%Y-%m-%d')
    end_date = pd.to_datetime(f'{end_year}-{end_month}-01', format='%Y-%m-%d')

    for file in files:
        df = process_csv(file, area)
        df = df[(df['Month_Year'] >= start_date) & (df['Month_Year'] <= end_date)]
        avg_confidence_mps = calculate_average_confidence(df, area)
        avg_mps_list.append(avg_confidence_mps)

    avg_confidence_combined = pd.concat(avg_mps_list).groupby(area)['Confidence'].mean().reset_index()
    avg_confidence_combined = avg_confidence_combined.sort_values(by='Confidence', ascending=True)

    return avg_confidence_combined


def average_confidence_over_time_spans(csv_files, area):
    avg_confidence_list = []

    for file in csv_files:
        df = process_csv(file, area)
        avg_confidence = calculate_average_confidence(df, area)
        avg_confidence_list.append(avg_confidence)

    avg_conf = pd.concat(avg_confidence_list).groupby(area)['Confidence'].mean().reset_index()
    avg_conf = avg_conf.sort_values(by='Confidence', ascending=True)

    return avg_conf


def calculate_top_areas_per_month(df, area):
    top_areas_count = {}

    months = df['Month_Year'].unique()

    for month in months:
        month_df = df[df['Month_Year'] == month]
        top_areas = month_df.groupby(area)['Confidence'].mean().nlargest(5).index

        for a in top_areas:
            if a in top_areas_count:
                top_areas_count[a] += 1
            else:
                top_areas_count[a] = 1

    return top_areas_count


def calculate_smallest_areas_per_month(df, area):
    smallest_areas_count = {}

    months = df['Month_Year'].unique()

    for month in months:
        month_df = df[df['Month_Year'] == month]
        bot_areas = month_df.groupby(area)['Confidence'].mean().nsmallest(5).index

        for a in bot_areas:
            if a in smallest_areas_count:
                smallest_areas_count[a] += 1
            else:
                smallest_areas_count[a] = 1

    return smallest_areas_count


def plot_top_areas(csv_files, area):
    top_areas_combined = {}

    for file in csv_files:
        df = process_csv(file, area)
        top_areas_count = calculate_top_areas_per_month(df, area)

        for a, count in top_areas_count.items():
            if a in top_areas_combined:
                top_areas_combined[a] += count
            else:
                top_areas_combined[a] = count

    top_areas_sorted = sorted(top_areas_combined.items(), key=lambda item: item[1], reverse=True)[:5]
    area, counts = zip(*top_areas_sorted)

    plt.figure(figsize=(10, 6))
    plt.bar(area, counts, color='skyblue')
    plt.xlabel("Areas")
    plt.ylabel('Number of Times in Top 5')
    plt.title(f'Top 5 areas with Highest Confidence in MPS Per Month')
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.tight_layout()
    plt.show()


def plot_bot_areas(csv_files, area):
    smallest_areas_combined = {}

    for file in csv_files:
        df = process_csv(file, area)
        smallest_areas_count = calculate_smallest_areas_per_month(df, area)

        for a, count in smallest_areas_count.items():
            if a in smallest_areas_combined:
                smallest_areas_combined[a] += count
            else:
                smallest_areas_combined[a] = count

    smallest_areas_sorted = sorted(smallest_areas_combined.items(), key=lambda item: item[1], reverse=True)[:5]
    area, counts = zip(*smallest_areas_sorted)

    plt.figure(figsize=(10, 6))
    plt.bar(area, counts, color='skyblue')
    plt.xlabel("Areas")
    plt.ylabel('Number of Times in Bottom 5')
    plt.title(f'Top 5 areas with Lowest Confidence in MPS Per Month')
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.tight_layout()
    plt.show()


ward = 'ward_n'
borough = 'C2'
csv = ['DC2_data/pas_data_ward_level/PAS_ward_level_FY_15_17.csv', 'DC2_data/pas_data_ward_level/PAS_ward_level_FY_17_18.csv', 'DC2_data/pas_data_ward_level/PAS_ward_level_FY_18_19.csv', 'DC2_data/pas_data_ward_level/PAS_ward_level_FY_19_20.csv']
start_month = 1
start_year = 2015
end_month = 12
end_year = 2020