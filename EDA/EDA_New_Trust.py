import pandas as pd


def process_csv(input_file, area):
    df = pd.read_csv(input_file)

    df = df[[area, 'NQ135BD']]

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

    df = df[df[area] != 'NA']
    df = df.dropna(subset=[area])

    return df


def calculate_average_mps(df, area):
    df['NQ135BD'] = pd.to_numeric(df['NQ135BD'], errors='coerce')

    avg_trust_mps = df.groupby(area)['NQ135BD'].mean().reset_index()
    avg_trust_mps = avg_trust_mps.rename(columns={'NQ135BD': 'Trust in MPS'})
    avg_trust_mps = avg_trust_mps.sort_values(by='Trust in MPS')

    return avg_trust_mps


def average_mps_over_time_spans(csv_files, area):
    avg_mps_list = []

    for file in csv_files:
        df = process_csv(file, area)
        avg_trust_mps = calculate_average_mps(df, area)
        avg_mps_list.append(avg_trust_mps)

    avg_mps = pd.concat(avg_mps_list).groupby(area)['Trust in MPS'].mean().reset_index()
    avg_mps = avg_mps.sort_values(by='Trust in MPS', ascending=True)

    return avg_mps


csv_files = ['DC2_data/pas_data_ward_level/PAS_ward_level_FY_15_17.csv', 'DC2_data/pas_data_ward_level/PAS_ward_level_FY_17_18.csv', 'DC2_data/pas_data_ward_level/PAS_ward_level_FY_18_19.csv', 'DC2_data/pas_data_ward_level/PAS_ward_level_FY_19_20.csv', 'DC2_data/pas_data_ward_level/PAS_ward_level_FY_20_21.csv'] # Insert paths to non-joined, ward-level PAS data
ward = 'ward_n'
borough = 'C2'
borough_2021 = 'Borough'
neighbourhood = 'BOROUGHNEIGHBOURHOOD'
avg_mps_over_time_spans = average_mps_over_time_spans(csv_files, neighbourhood)
print(avg_mps_over_time_spans)
