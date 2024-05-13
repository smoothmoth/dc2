import pandas as pd
import numpy as np
from typing import List
from police_api import PoliceAPI
import re


def one_hot_encode_categories(df: pd.DataFrame, column_names: List[str]) -> pd.DataFrame:
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


def get_boroughs_from_LSOA(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame  with an additional column "Borough"
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


def aggregate_row_counts(df: pd.DataFrame, column_names: List[str], new_column_name: str) -> pd.DataFrame:
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
    coords = df[["Latitude", "Longitude"]]

    def get_neighbour_id(lat, lon):
        if lat is None or lon is None:
            return None
        else:
            return api.locate_neighbourhood(lat=lat, lng=lon).id

    def get_neighbour_name(lat, lon):
        if lat is None or lon is None:
            return None
        else:
            return api.locate_neighbourhood(lat=lat, lng=lon).nm

    df["neighbourhood_id"] = coords.apply(
        lambda x: get_neighbour_id(coords["Latitude"], coords["Longitude"])
    )
    df["neighbourhood_name"] = coords.apply(
        lambda x: get_neighbour_name(coords["Latitude"], coords["Longitude"])
    )

    return df
