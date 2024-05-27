import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from police_api import PoliceAPI
import re
import geopandas as gpd
import json


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


def add_wards_old(df: pd.DataFrame, path_to_PAS: str) -> pd.DataFrame:
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


def add_wards(df: pd.DataFrame, path_to_ward_geojson: str) -> pd.DataFrame:
    """
    Adds columns for ward name and id.
    :param df: DataFrame on which to perform the operation
    :return: Original dataframe with two additional columns: one for ward ID, one for ward name
    """
    with open(path_to_ward_geojson) as f:
        geo = json.load(f)
        geodf = gpd.GeoDataFrame.from_features(geo)
    gdf_df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude), crs="EPSG:4326")
    sj = gpd.sjoin(left_df=gdf_df, right_df=geodf[["name", "code","geometry"]], how="left", predicate="intersects")
    sj['name'] = sj['name'].str.strip()
    sj_2 = sj.drop(columns=["index_right"]).copy()
    sj_3 = sj_2.dropna(subset=["name", "code"]).copy()
    sj_out = sj_3.rename(columns = {'name':'Ward name', 'code': 'Ward code'}).copy()

    return sj_out


def add_boroughs(df: pd.DataFrame, path_to_borough_geojson: str) -> pd.DataFrame:
    """
    Adds columns for borough name and id.
    :param df: DataFrame on which to perform the operation
    :return: Original dataframe with two additional columns: one for borough ID, one for borough name
    """
    with open(path_to_borough_geojson) as f:
        geo = json.load(f)
        geodf = gpd.GeoDataFrame.from_features(geo)
    gdf_df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude), crs="EPSG:4326")
    sj = gpd.sjoin(left_df=gdf_df, right_df=geodf[["name", "CODE","geometry"]], how="left", predicate="intersects")
    sj['name'] = sj['name'].str.strip()
    sj_2 = sj.drop(columns=["index_right"]).copy()
    sj_3 = sj_2.dropna(subset=["name", "CODE"]).copy()
    sj_out = sj_3.rename(columns ={'name':'Borough name', 'CODE': 'Borough code'}).copy()

    return sj_out 


def add_other_datasets(prepared_street: pd.DataFrame, path_to_econ: str, path_to_jobs: str) -> pd.DataFrame:
    """
    Adds information on economic factors (average borough pay and job density) to a DataFrame (should be a prepared df_street)
    :param prepared_street: Preprocessed df_street
    :param path_to_econ: path to the economic dataset
    :param path_to_jobs: path to the job density dataset
    :returns: A modified original DataFrame, now with average pay and job density per borough
    """
    prepared_street = prepared_street.replace({'Borough name':{'City of Westminster': 'Westminster'}})

    data_econ = pd.read_excel(path_to_econ, sheet_name='Total, Hourly')
    data_econ = data_econ.iloc[3:35,[1,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42]].reset_index().drop(columns='index').copy()
    data_econ = data_econ.melt(id_vars=["Area"], var_name='Year', value_name='Pay').copy()

    data_jobs = pd.read_excel(path_to_jobs, sheet_name='Jobs Density')
    data_jobs = data_jobs.iloc[2:34, 1:].reset_index().drop(columns='index').copy()
    data_jobs = data_jobs.melt(id_vars=["Area"], var_name='Year', value_name='jobDensity').copy()

    merged = pd.merge(prepared_street, data_econ, how='left', left_on=["Year","Borough name"], right_on=["Year", "Area"]).drop(columns='Area').copy()
    merged_out = pd.merge(merged , data_jobs, how='left', left_on=["Year","Borough name"], right_on=["Year", "Area"]).drop(columns='Area').copy()

    return merged_out
    

def clean_police_uk_crime_datasets(df_street: pd.DataFrame, df_search: pd.DataFrame) -> Tuple[pd.DataFrame]:
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

    # Recoding "Month" into pd.Period data type; adding "Year" column
    df_street_2["Year"] = pd.to_datetime(df_street_2['Month'], format='%Y-%m').dt.to_period("Y")
    df_search_2["Year"] = pd.to_datetime(df_search_2['Date'], format='%Y-%m', exact=False).dt.to_period("Y")
    df_street_2["Month"] = pd.to_datetime(df_street_2['Month'], format='%Y-%m').dt.to_period("M")
    df_search_2["Month"] = pd.to_datetime(df_search_2['Date'], format='%Y-%m', exact=False).dt.to_period("M")
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

    return df_street_final, df_search_final


def prepare_police_uk_crime_datasets(
        df_street: pd.DataFrame, 
        df_search: pd.DataFrame,   
        path_to_ward_geojson: str,
        path_to_borough_geojson: str,
        classify_search_dummies: bool = True,
        classify_street_dummies: bool = True,
        ) -> Tuple[pd.DataFrame]:
    """
    Prepares the police.uk crime data (more specifically: street and stop_and_search data) for statistical analysis.
    :param df_street: DataFrame containing the streets data
    :param df_search: DataFrame containing the stop_and_search data
    :param path_to_pas_data: Path top the folder containing all PAS tables
    :return: a Dictionary of 8 dataframes: one per a choice between: street/search data; aggregation by year or month; aggregation by ward or borough 
    """

    # Cleaning the data
    df_street_clean, df_search_clean = clean_police_uk_crime_datasets(df_street, df_search)
    print("DATA CLEANED")

    # Add "wards" column based on Latitude and Longitude
    df_street_1 = add_wards(df_street_clean, path_to_ward_geojson);
    df_search_1 = add_wards(df_search_clean, path_to_ward_geojson);
    print("WARDS ADDED")

    # Add "Borough" column based on Latitude and Longitude
    df_street_2 = add_boroughs(df_street_1, path_to_borough_geojson);
    df_search_2 = add_boroughs(df_search_1, path_to_borough_geojson);
    print("BOROUGHS ADDED")


    # Make a one-hot-encoding for relevant categories
    df_street_3 = one_hot_encode_categories(df_street_2, column_names=[
        "Crime type", "Last outcome category"
    ])
    df_search_3 = one_hot_encode_categories(df_search_2, column_names=[
        "Gender", "Age range", "Officer-defined ethnicity", "Legislation", "Outcome"
    ])
    
    df_out_search = df_search_3.copy()
    df_out_street = df_street_3.copy()

    if classify_search_dummies:
        # Classify "Reason for searching" into one of: Weapons; Drugs; Other based on Legislation column
        df_search_cls = aggregate_column_counts(df_out_search, [
            'Police and Criminal Evidence Act 1984 (section 1)',
            'Criminal Justice Act 1988 (section 139B)',
            'Criminal Justice and Public Order Act 1994 (section 60)'
            ], 'searchReasonCriminal').copy()
        
        df_search_cls_2 = df_search_cls.copy()
        df_search_cls_2['searchReasonDrugs'] = df_search_cls['Firearms Act 1968 (section 47)']
        df_search_cls_2['searchReasonFirearms'] = df_search_cls['Misuse of Drugs Act 1971 (section 23)']
        
        # Classify "If person should have been searched" based on outcome of search
        df_search_cls_3 = aggregate_column_counts(df_search_cls_2, [
            'Nothing found - no further action', 
            'A no further action disposal'
            ], 'outcomeUnsuitableForSearch').copy()
        df_search_cls_4 = aggregate_column_counts(df_search_cls_3, [
            'Offender given drugs possession warning', 'Suspect arrested',
            'Local resolution', 'Offender given penalty notice',
            'Suspect summonsed to court', 'Offender cautioned',
            'Article found - Detailed outcome unavailable','Arrest',
            'Khat or Cannabis warning', 'Community resolution',
            'Summons / charged by post', 'Penalty Notice for Disorder',
            'Caution (simple or conditional)'
        ], 'outcomeSuitableForSearch').copy()

        df_out_search = df_search_cls_4.copy()
        print(f"List of new search columns: {df_out_search.columns}")


    if classify_street_dummies:
        # Classify "Crime type" based on perceived severity/ harm done
        df_street_cls = aggregate_column_counts(df_out_street, [
            'Vehicle crime', 
            'Theft from the person', 
            'Shoplifting',
            'Bicycle theft',
            'Burglary',
            'Robbery',
            'Other theft'
        ], 'crimeTheft')
        df_street_cls_2 = aggregate_column_counts(df_street_cls, [
            'Violence and sexual offences',
            'Violent crime',
        ], 'crimeViolence')
        df_street_cls_3 = aggregate_column_counts(df_street_cls_2, [
            'Anti-social behaviour',
            'Criminal damage and arson',
            'Public disorder and weapons',
            'Public order',
            'Possession of weapons',
            'Drugs'
        ], 'crimePublicDisorder')

        df_street_cls_3['crimeOther'] = df_street_cls_3['Other crime']

        # Classify "Last outcome category"
        df_street_cls_4 = aggregate_column_counts(df_street_cls_3,[
            'Court result unavailable', 
            'Court case unable to proceed', 
            'Awaiting court outcome', 
            'Formal action is not in the public interest', 
            'Unable to prosecute suspect', 
            'Defendant sent to Crown Court'
        ], "resolutionNo").copy()
        df_street_cls_5 = aggregate_column_counts(df_street_cls_4,[
            'Offender sent to prison',
            'Offender given community sentence', 
            'Local resolution',
            'Offender given penalty notice',
            'Offender given a drugs possession warning',
            'Offender given conditional discharge',
            'Defendant found not guilty', 
            'Offender given a caution',
            'Offender fined', 
            'Offender given suspended prison sentence',
            'Offender deprived of property',
            'Offender otherwise dealt with',
            'Offender ordered to pay compensation',
            'Suspect charged as part of another case',
            'Offender given absolute discharge',
        ], "resolutionYes").copy()

       

        df_out_street = df_street_cls_5.copy()
        print(f"List of new street columns: {df_out_street.columns}")
    
    

    return df_out_street, df_out_search



def aggregate_police_uk_data(
        prepared_street: pd.DataFrame, 
        prepared_search: pd.DataFrame,
        path_to_econ: pd.DataFrame,
        path_to_jobs: pd.DataFrame
        ) -> Dict[str, pd.DataFrame]:
    """
    Aggregates data for analysis.
    :param prepared street: a DataFrame of crime data that was preprocessed by prepare_police_uk_crime_datasets
    :param prepared search; a DataFrame of search data prepare_police_uk_crime_datasets
    :param path_to_econ: path to the economic dataset
    :param path_to_jobs: path to the job density dataset
    :returns: A dictionary containing DataFrames with different levels of data aggregation
    """
    outdct = {}

    # Modify data to include additional variables and for consistency
    prepared_street = add_other_datasets(prepared_street, path_to_econ, path_to_jobs).copy()
    prepared_search = prepared_search.replace({'Borough name':{'City of Westminster': 'Westminster'}}).copy()

    # Create aggregation mapper for street data
    street_agg_mapper = {}
    for column_name in prepared_street.columns:
        street_agg_mapper[f"{column_name}"] = ["sum"]
    for not_needed in ['Crime ID', 'Month', 'Longitude', 'Latitude', 'Location', 'LSOA code',
       'LSOA name', 'geometry', 'Ward name', 'Ward code','Borough name', 'Year',
       'Borough code']:
        del street_agg_mapper[not_needed]
    street_agg_mapper['Pay'] = ['first']
    street_agg_mapper['jobDensity'] = ['first']

    # Create the dataframes for street data
    df1 = prepared_street.groupby(['Year', "Borough name"]).agg(street_agg_mapper).reset_index()
    df1.columns = [col_name[0] for col_name in df1.columns]
    outdct['street_year_borough'] = df1.copy()

    street_agg_mapper['Year'] = ['first']
    df2 = prepared_street.groupby(['Month', "Borough name"]).agg(street_agg_mapper).reset_index()
    df2.columns = [col_name[0] for col_name in df2.columns]
    outdct['street_month_borough'] = df2.copy()

    del street_agg_mapper['Year']
    street_agg_mapper['Borough name'] = ['first']
    df3 = prepared_street.groupby(['Year', "Ward name"]).agg(street_agg_mapper).reset_index()
    df3.columns = [col_name[0] for col_name in df3.columns]
    outdct['street_year_ward'] = df3.copy()
    
    street_agg_mapper['Year'] = ['first']
    df4 = prepared_street.groupby(['Month', "Ward name"]).agg(street_agg_mapper).reset_index()
    df4.columns = [col_name[0] for col_name in df4.columns]
    outdct['street_month_ward'] = df4.copy()

    # Create aggregation mapper for search data
    search_agg_mapper = {}
    for column_name in prepared_search.columns:
        search_agg_mapper[f"{column_name}"] = ["sum"]
    for not_needed in ['Type', 'Latitude', 'Longitude', 'Month', 'geometry',
       'Ward name', 'Ward code', 'Borough code','Borough name', 'Year']:
        del search_agg_mapper[not_needed]

    # Create the dataframes for search data

    df5 = prepared_search.groupby(['Year', "Borough name"]).agg(search_agg_mapper).reset_index()
    df5.columns = [col_name[0] for col_name in df5.columns]
    outdct['search_year_borough'] = df5.copy()

    search_agg_mapper['Year'] = ['first']
    df6 = prepared_search.groupby(['Month', "Borough name"]).agg(search_agg_mapper).reset_index()
    df6.columns = [col_name[0] for col_name in df6.columns]
    outdct['search_month_borough'] = df6.copy()

    del search_agg_mapper['Year']
    search_agg_mapper['Borough name'] = ['first']
    df7 = prepared_search.groupby(['Year', "Ward name"]).agg(search_agg_mapper).reset_index()
    df7.columns = [col_name[0] for col_name in df7.columns]
    outdct['search_year_ward'] = df7.copy()
    
    search_agg_mapper['Year'] = ['first']
    df8 = prepared_search.groupby(['Month', "Ward name"]).agg(search_agg_mapper).reset_index()
    df8.columns = [col_name[0] for col_name in df8.columns]
    outdct['search_month_ward'] = df8.copy()

    return outdct  
    


def save_aggregated_data_to_csv(
        prepared_street: pd.DataFrame, 
        prepared_search: pd.DataFrame,
        path_to_econ: pd.DataFrame,
        path_to_jobs: pd.DataFrame) -> None:
    """
    Saves the aggregated data to csv files (8 files, one per level of aggregation)
    :param prepared street: a DataFrame of crime data that was preprocessed by prepare_police_uk_crime_datasets
    :param prepared search; a DataFrame of search data prepare_police_uk_crime_datasets
    :param path_to_econ: path to the economic dataset
    :param path_to_jobs: path to the job density dataset
    """
    dct: Dict = aggregate_police_uk_data(prepared_street, prepared_search, path_to_econ, path_to_jobs)
    for key, value in dct.items():
        value.to_csv(f"{key}.csv")

