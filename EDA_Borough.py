import pandas as pd

def highest_x_proportion(chosen_measure, start_year, end_year, x):
    df = pd.read_excel('DC2_data/PAS_T&Cdashboard_to Q3 23-24.xlsx', sheet_name='Borough') # insert the path to the original, publicly available PAS

    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

    filtered_df = df[(df['Measure'] == chosen_measure) &
                     (df['Date'].dt.year >= start_year) &
                     (df['Date'].dt.year <= end_year)]

    avg_proportion_by_borough = filtered_df.groupby('Borough')['Proportion'].mean()

    lowest_x_boroughs = avg_proportion_by_borough.nlargest(x)

    return lowest_x_boroughs

def lowest_x_proportion(chosen_measure, start_year, end_year, x):
    df = pd.read_excel('DC2_data/PAS_T&Cdashboard_to Q3 23-24.xlsx', sheet_name='Borough') # insert the path to the original, publicly available PAS

    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

    filtered_df = df[(df['Measure'] == chosen_measure) &
                     (df['Date'].dt.year >= start_year) &
                     (df['Date'].dt.year <= end_year)]

    avg_proportion_by_borough = filtered_df.groupby('Borough')['Proportion'].mean()

    lowest_x_boroughs = avg_proportion_by_borough.nsmallest(x)

    return lowest_x_boroughs


def preprocess_borough_names(df):
    df['Borough'] = df['Borough'].str.lower()

    df['Borough'] = df['Borough'].replace('richmond upon thames', 'richmond upon thames')

    return df


def calculate_trust(df):
    df_filtered = df[['Date', 'Borough', 'Measure', 'Proportion']]

    pivot_table = df_filtered.pivot_table(index=['Date', 'Borough'], columns='Measure', values='Proportion')

    pivot_table.fillna(0, inplace=True)

    trust = 0.4 * pivot_table['\"Good Job\" local'] + 0.2 * pivot_table['Contact ward officer'] + 0.4 * pivot_table[
        'Treat everyone fairly']

    trust_df = pd.DataFrame({'Trust': trust})

    trust_df.reset_index(inplace=True)

    return trust_df

def top_boroughs_avg_trust(trust_df, start_year, end_year, x):
    trust_df = preprocess_borough_names(trust_df)

    trust_df['Date'] = pd.to_datetime(trust_df['Date'])

    filtered_df = trust_df[(trust_df['Date'].dt.year >= start_year) & (trust_df['Date'].dt.year <= end_year)]

    avg_trust = filtered_df.groupby('Borough')['Trust'].mean().reset_index()

    sorted_df = avg_trust.sort_values(by='Trust', ascending=False)

    return sorted_df.head(x)

def bot_boroughs_avg_trust(trust_df, start_year, end_year, x):
    trust_df = preprocess_borough_names(trust_df)

    trust_df['Date'] = pd.to_datetime(trust_df['Date'])

    filtered_df = trust_df[(trust_df['Date'].dt.year >= start_year) & (trust_df['Date'].dt.year <= end_year)]

    avg_trust = filtered_df.groupby('Borough')['Trust'].mean().reset_index()

    sorted_df = avg_trust.sort_values(by='Trust', ascending=True)

    return sorted_df.head(x)


def calculate_confidence(df):
    df_filtered = df[['Date', 'Borough', 'Measure', 'Proportion']]

    pivot_table = df_filtered.pivot_table(index=['Date', 'Borough'], columns='Measure', values='Proportion')

    pivot_table.fillna(0, inplace=True)

    confidence = 0.3 * pivot_table['\"Good Job\" local'] + 0.1 * pivot_table['Informed local'] + 0.1 * pivot_table[
        'Listen to concerns'] + 0.1 * pivot_table['Relied on to be there'] + 0.3 * pivot_table['Treat everyone fairly'] \
            + 0.1 * pivot_table['Understand issues']

    confidence_df = pd.DataFrame({'Confidence': confidence})

    confidence_df.reset_index(inplace=True)

    return confidence_df

def top_boroughs_avg_confidence(confidence_df, start_year, end_year, x):
    confidence_df = preprocess_borough_names(confidence_df)

    confidence_df['Date'] = pd.to_datetime(confidence_df['Date'])

    filtered_df = confidence_df[(confidence_df['Date'].dt.year >= start_year) & (confidence_df['Date'].dt.year <= end_year)]

    avg_confidence = filtered_df.groupby('Borough')['Confidence'].mean().reset_index()

    sorted_df = avg_confidence.sort_values(by='Confidence', ascending=False)

    return sorted_df.head(x)

def bot_boroughs_avg_confidence(confidence_df, start_year, end_year, x):
    confidence_df = preprocess_borough_names(confidence_df)

    confidence_df['Date'] = pd.to_datetime(confidence_df['Date'])

    filtered_df = confidence_df[(confidence_df['Date'].dt.year >= start_year) & (confidence_df['Date'].dt.year <= end_year)]

    avg_confidence = filtered_df.groupby('Borough')['Confidence'].mean().reset_index()

    sorted_df = avg_confidence.sort_values(by='Confidence', ascending=True)

    return sorted_df.head(x)


df = pd.read_excel('DC2_data/PAS_T&Cdashboard_to Q3 23-24.xlsx', sheet_name='Borough') # insert the path to the original, publicly available PAS
confidence_df = calculate_confidence(df)

top_boroughs = top_boroughs_avg_confidence(confidence_df, 2014, 2018, 5)
print(top_boroughs)