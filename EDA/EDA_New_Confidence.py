import pandas as pd
import numpy as np

def process_csv(input_file, area):
    df = pd.read_csv(input_file)

    df = df[[area, 'Q60', 'Q61', 'Q62A', 'Q62C', 'Q62F', 'Q62TG', 'NQ135BH', 'Q131', 'Q133']]

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


    df[area] = df[area].str.strip()

    df = df[df[area] != 'N/A']
    df = df.dropna(subset=[area])

    df.replace("", np.nan, inplace=True)

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

    return df[[area, 'Confidence']]


def calculate_average_confidence(df, area):
    df['Confidence'] = pd.to_numeric(df['Confidence'], errors='coerce')

    avg_confidence = df.groupby(area)['Confidence'].mean().reset_index()
    avg_confidence = avg_confidence.sort_values(by='Confidence')

    return avg_confidence


def average_confidence_over_time_spans(csv_files, area):
    avg_confidence_list = []

    for file in csv_files:
        df = process_csv(file, area)
        avg_confidence = calculate_average_confidence(df, area)
        avg_confidence_list.append(avg_confidence)

    avg_conf = pd.concat(avg_confidence_list).groupby(area)['Confidence'].mean().reset_index()
    avg_conf = avg_conf.sort_values(by='Confidence', ascending=True)

    return avg_conf


ward = 'ward_n'
borough = 'C2'
borough_2021 = 'Borough'
neighbourhood = 'BOROUGHNEIGHBOURHOOD'
csv = ['DC2_data/pas_data_ward_level/PAS_ward_level_FY_15_17.csv', 'DC2_data/pas_data_ward_level/PAS_ward_level_FY_17_18.csv', 'DC2_data/pas_data_ward_level/PAS_ward_level_FY_18_19.csv', 'DC2_data/pas_data_ward_level/PAS_ward_level_FY_19_20.csv', 'DC2_data/pas_data_ward_level/PAS_ward_level_FY_20_21.csv'] # Insert paths to non-joined, ward-level PAS data

print(average_confidence_over_time_spans(csv, neighbourhood))