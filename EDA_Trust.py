import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


def process_csv(input_file, area):
    df = pd.read_csv(input_file)

    df = df[[area, 'NQ135BD', 'MONTH']]

    value_mapping = {
        'Strongly agree': 1,
        'Tend to agree': 0.75,
        'Neither agree nor disagree': 0.5,
        'Tend to disagree': 0.25,
        'Strongly disagree': 0,
        'NA': 'NA'
    }
    df['NQ135BD'] = df['NQ135BD'].map(value_mapping)

    df[area] = df[area].str.strip()

    df = df[df[area].notna() & (df[area] != '#N/A')]

    df['NQ135BD'] = pd.to_numeric(df['NQ135BD'], errors='coerce')
    df = df[df['NQ135BD'].notna()]

    df['Month_Year'] = df['MONTH'].str.extract(r'(\d{2}) \((\w+ \d{4})\)', expand=True)[1]
    df['Month_Year'] = pd.to_datetime(df['Month_Year'], format='%b %Y')

    return df


def calculate_average_mps(df, area):
    df['NQ135BD'] = pd.to_numeric(df['NQ135BD'], errors='coerce')

    avg_trust_mps = df.groupby(area)['NQ135BD'].mean().reset_index()
    avg_trust_mps = avg_trust_mps.rename(columns={'NQ135BD': 'Trust in MPS'})
    avg_trust_mps = avg_trust_mps.sort_values(by='Trust in MPS')

    return avg_trust_mps


def average_trust_over_time(files, start_month, start_year, end_month, end_year, area):
    avg_mps_list = []
    start_date = pd.to_datetime(f'{start_year}-{start_month}-01', format='%Y-%m-%d')
    end_date = pd.to_datetime(f'{end_year}-{end_month}-01', format='%Y-%m-%d')

    for file in files:
        df = process_csv(file, area)
        df = df[(df['Month_Year'] >= start_date) & (df['Month_Year'] <= end_date)]
        avg_trust_mps = calculate_average_mps(df, area)
        avg_mps_list.append(avg_trust_mps)

    avg_mps_combined = pd.concat(avg_mps_list).groupby(area)['Trust in MPS'].mean().reset_index()
    avg_mps_combined = avg_mps_combined.sort_values(by='Trust in MPS', ascending=True)

    return avg_mps_combined


def calculate_top_areas_per_month(df, area):
    top_areas_count = {}

    months = df['Month_Year'].unique()

    for month in months:
        month_df = df[df['Month_Year'] == month]
        top_areas = month_df.groupby(area)['NQ135BD'].mean().nlargest(5).index

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
        bot_areas = month_df.groupby(area)['NQ135BD'].mean().nsmallest(5).index

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
    plt.title(f'Top 5 areas with Highest Trust in MPS Per Month')
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
    plt.title(f'Top 5 areas with Lowest Trust in MPS Per Month')
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.tight_layout()
    plt.show()


csv = ['DC2_data/pas_data_ward_level/PAS_ward_level_FY_15_17.csv', 'DC2_data/pas_data_ward_level/PAS_ward_level_FY_17_18.csv', 'DC2_data/pas_data_ward_level/PAS_ward_level_FY_18_19.csv', 'DC2_data/pas_data_ward_level/PAS_ward_level_FY_19_20.csv']
ward = 'ward_n'
borough = 'C2'
start_month = 1
start_year = 2015
end_month = 12
end_year = 2020