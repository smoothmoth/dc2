import pandas as pd
import numpy as np
from typing import List, Tuple
from police_api import PoliceAPI
import re


def one_hot_encode_categories(df: pd.DataFrame, column_names: List[str]) -> pd.DataFrame:  # Code adapted from what
    # Hetvi wrote
    """
    One-hot encodes categorical data from specified columns
    :param df: DataFrame on which to perform the operation
    :param column_names: columns, each row of which will be added up
    :return: a DataFrame with one-hot-encodes specified columns
    """
    for column in column_names:
        one_hot_encoded = pd.get_dummies(df[column])
        one_hot_encoded = one_hot_encoded.astype(int)
        df = pd.concat([df, one_hot_encoded], axis=1)
    df = df.drop(columns=column_names)
    return df


def get_boroughs_from_LSOA(df: pd.DataFrame) -> pd.DataFrame:  # Code adapted from what Hetvi wrote
    """
    Returns a DataFrame with an additional column "Borough"
    :param df: a DataFrame with LSOA_name being one of the columns
    :return: a DataFrame  with an additional column "Borough"
    """
    pattern = r'^[^\d]+'

    # Function to extract the name using regex
    def extract_name(text):
        match = re.search(pattern, text)
        if match:
            return match.group(0)
        else:
            return "No match found."

    # Apply the function to the DataFrame column
    df['Borough'] = df['LSOA name'].apply(extract_name)

    return df


def aggregate_column_counts(df: pd.DataFrame, column_names: List[str], new_column_name: str) -> pd.DataFrame:
    """
    Aggregates data by adding values in each row of the specified columns and putting the resulting sum in a new column.
    Suitable for aggregating dummy variable categories to benefit from grouping (e.g., you can use the function on
    columns made for "Violent crime" and "Violence and sexual offences" to arrive at "Violent Crime" category.
    :param df: DataFrame on which to perform the operation
    :param column_names: columns, each row of which will be added up
    :param new_column_name: name of the new column in which the sum of values of columns specified in column_names will
    be placed
    :return: a DataFrame with a new column called as specified in new_column_name, containing a sum of values from
    columns in column_names, per row.
    """
    subset: pd.DataFrame = df[column_names].copy()
    df[new_column_name] = subset.aggregate('sum', axis=1)
    return df


def add_neighbourhoods(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds columns for neighbourhood name and id
    :param df: DataFrame on which to perform the operation
    :return: Original dataframe with two additional columns: one for neighbourhood ID, one for neighbourhood name
    """
    api = PoliceAPI()

    def get_neighbour_id(lat, lon):
        if lat is None or lon is None:
            return None
        else:
            return api.locate_neighbourhood(lat=lat, lng=lon).id

    def get_neighbour_name(lat, lon):
        if lat is None or lon is None:
            return None
        else:
            return api.locate_neighbourhood(lat=lat, lng=lon).name

    dct_index = {}
    dct_name = {}
    df_temp = df.copy()
    df_temp["Cords"] = df_temp[['Latitude', 'Longitude']].apply(tuple, axis=1)
    print("Tuples complete")
    cnt = 0
    uniq = df_temp["Cords"].unique()
    print(len(uniq))
    print(len(df["LSOA code"].unique()))
    for i in uniq:
        dct_index[i] = get_neighbour_id(i[0], i[1])
        # dct_name[i] = get_neighbour_name(i[0], i[1])
        cnt += 1
        print(cnt)
    print(dct_index)
    # print(dct_name)
    df_temp["Neighbourhood ID"] = df_temp["Cords"].map(dct_index)
    print('Index map complete')
    # df_temp["Neighbourhood name"] = df_temp["Cords"].map(dct_name)
    # print('Name map complete')
    df["Neighbourhood ID"] = df_temp["Neighbourhood ID"]
    # df["Neighbourhood name"] = df_temp["Neighbourhood name"]


    return df


def add_wards(df: pd.DataFrame, path_to_PAS: str) -> pd.DataFrame:
    """
    Adds columns for ward name and id.
    :param df: DataFrame on which to perform the operation
    :return: Original dataframe with two additional columns: one for neighbourhood ID, one for neighbourhood name
    """
    pas_df_15_17 = pd.read_csv(path_to_PAS + "\PAS_ward_level_FY_15_17.csv").copy()
    pas_df_17_18 = pd.read_csv(path_to_PAS + "\PAS_ward_level_FY_17_18.csv").copy()
    pas_df_18_19 = pd.read_csv(path_to_PAS + "\PAS_ward_level_FY_18_19.csv").copy()
    pas_df_19_20 = pd.read_csv(path_to_PAS + "\PAS_ward_level_FY_19_20.csv").copy()
    pas_df_20_21 = pd.read_csv(path_to_PAS + "\PAS_ward_level_FY_20_21.csv").copy()

    df_15_17 = df[(df["Month"] >="2015-04") & (df["Month"] <="2017-03")].copy()
    df_17_18 = df[(df["Month"] >="2017-04") & (df["Month"] <="2018-03")].copy()
    df_18_19 = df[(df["Month"] >="2018-04") & (df["Month"] <="2019-03")].copy()
    df_19_20 = df[(df["Month"] >="2019-04") & (df["Month"] <="2020-03")].copy()
    df_20_21 = df[(df["Month"] >="2020-04") & (df["Month"] <="2021-03")].copy()

    pas_df_list = [pas_df_15_17, pas_df_17_18, pas_df_18_19, pas_df_19_20, pas_df_20_21]
    df_list = [df_15_17, df_17_18, df_18_19, df_19_20, df_20_21]

    for i in range(4):
        dct_c = {}
        dct_n = {}
        d = df_list[i]
        p = pas_df_list[i]
        p_uniq = p.drop_duplicates(subset = ['SOA1', 'ward'])
        for row in p_uniq[['SOA1', 'ward', 'ward_n']].iterrows():
            r = row[1]['SOA1'].strip()
            w = row[1]['ward'].strip()
            n = row[1]['ward_n'].strip()
            dct_c[r] = w
            dct_n[r] = n
        d['ward'] = d['LSOA code'].map(dct_c)
        d['ward_name'] = d['LSOA code'].map(dct_n)
    na = pd.Series(['Not Available']*len(df_20_21))
    df_20_21['ward'] = na
    df_20_21['ward_name'] = na

    out_df =  pd.concat(df_list).copy()
    out_df2 = out_df.dropna(subset=['ward'])

    return out_df2


def add_economic_variables(df: pd.DataFrame) -> pd.DataFrame:
    """
    """


def clean_police_uk_crime_datasets(df_street: pd.DataFrame, df_search: pd.DataFrame) -> List[pd.DataFrame]:
    """
    Cleans the police.uk crime data (more specifically: street and stop_and_search data)
    :param df_street: DataFrame containing the streets data
    :param df_search: DataFrame containing the stop_and_search data
    :return: a list [df_street, df_search], each of these clean
    """
    # Deleting all the columns that have insufficient nr of unique values
    df_street_1 = df_street.drop(columns=["Context", "Reported by", "Falls within"]).copy()
    df_search_1 = df_search.drop(
        columns=["Part of a policing operation", "Policing operation", "Outcome linked to object of search",
                 "Removal of more than just outer clothing", "Self-defined ethnicity", "Object of search"]).copy()

    # Removing duplicate rows
    df_street_2 = df_street_1.drop_duplicates().copy()
    df_search_2 = df_search_1.drop_duplicates().copy()

    # Recoding "Month" into pd.Period data type
    df_street_2["Month"] = pd.to_datetime(df_street_2['Month'], format='%Y-%m').dt.to_period("m")
    df_search_2["Month"] = pd.to_datetime(df_search_2['Date'], format='%Y-%m', exact=False).dt.to_period("m")
    df_search_2 = df_search_2.drop("Date", axis=1)

    # Remove rows with null values in some relevant columns
    df_street_3 = df_street_2.dropna(subset=["Latitude"]).copy()
    df_search_3 = df_search_2.dropna(subset=["Latitude", "Gender", "Age range", "Officer-defined ethnicity"]).copy()
    df_street_3 = df_street_3.fillna(value={"Last outcome category": 'Status update unavailable'})

    print(f"Proportion of rows in clean data relative to original data.\nStreet:{len(df_street_3) / len(df_street)}"
          f"\nStop-and-Search: {len(df_search_3) / len(df_search)}")
    print("---")
    print(f"Number of NA values still present in the data.\nStreet:{df_street_3.isnull().sum()}"
          f"\nSearch:{df_search_3.isnull().sum()} ")

    df_street_final = df_street_3.reset_index().drop('index', axis=1)
    df_search_final = df_search_3.reset_index().drop('index', axis=1)

    return [df_street_final, df_search_final]


def prepare_police_uk_crime_datasets(df_street: pd.DataFrame, df_search: pd.DataFrame, df_econ: pd.DataFrame,  path_to_pas_data: str) -> Tuple[ pd.DataFrame]:
    """
    Prepares the police.uk crime data (more specifically: street and stop_and_search data) for statistical analysis.
    :param df_street: DataFrame containing the streets data
    :param df_search: DataFrame containing the stop_and_search data
    :param path_to_pas_data: Path top the folder containing all PAS tables
    :return: a list [df_street, df_search], each ready for use in statistical analysis
    """

    # Cleaning the data
    df_street_clean, df_search_clean = clean_police_uk_crime_datasets(df_street, df_search)

    # Add "wards" column based on Latitude and Longitude
    df_street_1 = add_wards(df_street_clean, path_to_pas_data)
    df_search_1 = add_wards(df_search_clean, path_to_pas_data)

    # Add "Borough" column based on LSOA
    df_street_2 = get_boroughs_from_LSOA(df_street_1)
    df_search_2 = get_boroughs_from_LSOA(df_search_1)


    # Make a one-hot-encoding for relevant categories
    df_street_3 = one_hot_encode_categories(df_street_2, column_names=[
        "Crime type", "Last outcome category"
    ])
    df_search_3 = one_hot_encode_categories(df_search_2, column_names=[
        "Gender", "Age range", "Officer-defined ethnicity", "Legislation", "Outcome"
    ])
    print(f"Street data columns after encoding: {df_street_3.columns}")
    print(f"Search data columns after encoding: {df_search_3.columns}")

    # Classify "Reason for searching" into one of: Weapons; Drugs; Criminal based on Legislation column


    # Classify "Crime type" based on perceived severity/ harm done

    # Classify "If person should have been searched" based on outcome of search


df_street = pd.read_csv("D:\DC2_Output\metropolitan-street-combined.csv", low_memory=False)
df_search = pd.read_csv("D:\DC2_Output\metropolitan-stop-and-search.csv", low_memory=False)
clean_street, clean_search = clean_police_uk_crime_datasets(df_street, df_search)
# print(add_neighbourhoods(clean_street)["Neighbourhood name"])
# print(df_street.columns)
#clean_df = clean_police_uk_crime_datasets(df_street)
wards = add_wards(clean_street,"D:\DC2_Output\pas_data_ward_level")
print(wards)

