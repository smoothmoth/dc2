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



def further_clean_PAS(df_PAS: pd.DataFrame, recode: bool = True) -> pd.DataFrame:
    """
    Further cleans tha joined PAS dataset
    :param recode: whether to recode questions into numbers or not
    """

    # remove whitespaces from string entries
    for column in ['ward_n','C2']:
        df_PAS[column] = df_PAS[column].str.strip()
    
    # recode week into pd.Period
    df_PAS['Month'] = (df_PAS['MONTH'].str.split().str[1] + ' ' + df_PAS['MONTH'].str.split().str[2]).str.strip("()")
    df_PAS.drop(columns=['MONTH'])
    df_PAS['Year'] = pd.to_datetime(df_PAS['Month'], format='%b %Y').dt.to_period("Y")
    df_PAS['Month'] = pd.to_datetime(df_PAS['Month'], format='%b %Y').dt.to_period("M")

    if recode:
        # recode question variables into numbers

        # prepare mapping dictionary per question
        question_mappers_dct = {}
        question_mappers_dct['Q1'] = {
            '5 years but less than 10 years': 7.5,
            '30 years or more': 35,
            '2 years but less than 3 years': 2.5,
            '12 months but less than 2 years': 1.5,
            'Less than 12 months': 0.5,
            '20 years but less than 30 years': 25,
            '3 years but less than 5 years': 4,
            '10 years but less than 20 years':15
        }
        question_mappers_dct['Q13'] = {
            'Not very worried': 2,
            'Fairly worried': 3,
            'Not at all worried': 1,
            'Very worried': 4,
        }
        for q in ['Q60', 'Q61']:
            question_mappers_dct[q] = {
                'Good': 4,
                'Excellent': 5,
                'Fair': 3,
                'Very poor': 1, 
                'Poor': 2,
            }
        
        for q in ['Q62A', 'Q62C', 'Q62F', 'Q62TG', 'NQ135BD']:
            question_mappers_dct[q] = {
                'Tend to agree': 4,
                'Strongly agree': 5,
                'Tend to disagree': 2,
                'Neither agree nor disagree': 3,
                'Strongly disagree': 1
            }
        
        question_mappers_dct['NQ135BH'] = {
            'Tend to agree': 4,
            'Strongly agree': 5,
            'Tend to disagree': 2,
            'Neither agree nor disagree': 3,
            'Strongly disagree': 1,
            'Not Asked': np.nan,
            "Don't know": np.nan,
            'Refused': np.nan
            }
        
        question_mappers_dct['A121'] = {
            'Fairly confident':3,
            'Very confident': 4,
            'Not very confident': 2,
            'Not at all confident': 1,
        }

        for q in ['Q131', 'Q133']:
            question_mappers_dct[q] = {
            'Fairly well informed': 2, 
            'Not at all informed': 1, 
            'Very well informed': 3,
            }

        for column in question_mappers_dct:
            df_PAS[column] = df_PAS[column].map(question_mappers_dct[column])

    df_out = df_PAS[['ward_n', 'C2','Month', 'Year', 'Q1', 'Q13', 'Q60', 'Q61', 'Q62A', 'Q62C', 'Q62F', 'Q62TG', 'A121',
       'Q131', 'Q133', 'NQ135BD', 'NQ135BH']]
    
    if recode:
        for q in ['Q1', 'Q13', 'Q60', 'Q61', 'Q62A', 'Q62C', 'Q62F', 'Q62TG', 'A121',
        'Q131', 'Q133', 'NQ135BD', 'NQ135BH']:
            df_out[q] = df_out[["ward_n", q]].groupby("ward_n").transform(lambda x: x.fillna(x.mean()))

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

        def calculate_confidence(row): # Taken from Nabil's code
            total_weight = 0
            weighted_sum = 0
            for column, weight in weights.items():
                if pd.notnull(row[column]):
                    weighted_sum += row[column] * weight
                    total_weight += weight
            if total_weight == 0:
                return np.nan
            return weighted_sum / total_weight

        df_out['Confidence'] = df_out.apply(calculate_confidence, axis=1)

    df_out = df_out.rename(columns=
        {
            'C2':'Borough name', 
            'ward_n': 'Ward name', 
            #'ward': 'Ward code',
            'Q1': 'qLivedInAreaForYears', 
            'Q13':'qWorriedAboutCrimeInArea', 
            'Q60':'qGoodJobLocal', 
            'Q61': 'qGoodJobLondon', 
            'Q62A': 'qReliedOnToBeThere', 
            'Q62C':'qTreatEveryoneFairly', 
            'Q62F': 'qDealWithWhatMattersToTheCommunity',
            'Q62TG': 'qListenToConcerns', 
            'A121': 'qConfidentThatStopAndSearchFair', 
            'Q131': 'qInformedLocal', 
            'Q133':'qInformedLondon', 
            'NQ135BD': 'Trust', 
            'NQ135BH': 'qPoliceHeldAccountable'
            }
    )

    return df_out



def aggregate_PAS_data(clean_PAS: pd.DataFrame, confidence: bool = True) -> Dict['str', pd.DataFrame]:
    """
    Aggregates the PAS data.
    :param confidence: if including confidence is needed or not
    """
    outdct = {}

    # Define the mapper
    mapper = {}
    for q in [
        'qLivedInAreaForYears',
        'qWorriedAboutCrimeInArea',
        'qGoodJobLocal',
        'qGoodJobLondon',
        'qReliedOnToBeThere',
        'qTreatEveryoneFairly',
        'qDealWithWhatMattersToTheCommunity',
        'qListenToConcerns',
        'qConfidentThatStopAndSearchFair',
        'qInformedLocal',
        'qInformedLondon',
        'Trust',
        'qPoliceHeldAccountable',
        ]:
        mapper[q] = ['mean']
    if confidence:
        mapper['Confidence'] = ['mean']


    df1 = clean_PAS.groupby(['Year', "Borough name"]).agg(mapper).reset_index()
    df1.columns = [col_name[0] for col_name in df1.columns]
    outdct['PAS_year_borough'] = df1.copy()

    mapper['Year'] = ['first']
    df2 = clean_PAS.groupby(['Month', "Borough name"]).agg(mapper).reset_index()
    df2.columns = [col_name[0] for col_name in df2.columns]
    outdct['PAS_month_borough'] = df2.copy()

    del mapper['Year']
    mapper['Borough name'] = ['first']
    df3 = clean_PAS.groupby(['Year', "Ward name"]).agg(mapper).reset_index()
    df3.columns = [col_name[0] for col_name in df3.columns]
    outdct['PAS_year_ward'] = df3.copy()
    
    mapper['Year'] = ['first']
    df4 = clean_PAS.groupby(['Month', "Ward name"]).agg(mapper).reset_index()
    df4.columns = [col_name[0] for col_name in df4.columns]
    outdct['PAS_month_ward'] = df4.copy()

    return outdct



def join_data(
    aggregated_street: pd.DataFrame, 
    aggregated_search: pd.DataFrame,
    aggregated_PAS: pd.DataFrame,
    how_time: str = 'Month',
    how_space: str = 'Ward name',
    recode_to_period_PAS: bool = True
    ) -> pd.DataFrame:
    """
    Joins the prepared datasets, depending on the level of aggregation (to be specified in how_time and how_space)
    :param aggregated_street: Aggregated street data
    :param aggregated_search: Aggregated search data
    :param aggregated_PAS: Aggregated PAS data
    :param how_time: one of "Month", "Year"
    :param how_space: one of "Ward name", "Borough name"
    :param recode_to_period_PAS: Whether to recode PAS Month to period or not in the process
    :returns: a DataFrame that is a join of the three input dataframes.
    """
    aggregated_street[how_time] = pd.to_datetime(aggregated_street[how_time], format='%Y-%m').dt.to_period("M")
    aggregated_search[how_time] = pd.to_datetime(aggregated_search[how_time], format='%Y-%m').dt.to_period("M")
    if recode_to_period_PAS:
        aggregated_PAS[how_time] = pd.to_datetime(aggregated_PAS[how_time], format='%Y-%m').dt.to_period("M")

    print(aggregated_search[how_time].dtype)
    start1 = aggregated_street[how_time].min()
    start2 = aggregated_search[how_time].min()
    start3 = aggregated_PAS[how_time].min()

    # Get ending measurement dates
    end1 = aggregated_street[how_time].max()
    end2 = aggregated_search[how_time].max()
    end3= aggregated_PAS[how_time].max()

    start_measurement = max(start1, start2, start3)
    end_measurement = min(end1, end2, end3)

    print(f"Start date: {start_measurement}; end date: {end_measurement}")

    aggregated_street = aggregated_street[(aggregated_street[how_time] >= start_measurement) & (aggregated_street[how_time] <= end_measurement)]
    aggregated_search = aggregated_search[(aggregated_search[how_time] >= start_measurement) & (aggregated_search[how_time] <= end_measurement)]
    aggregated_PAS = aggregated_PAS[(aggregated_PAS[how_time] >= start_measurement) & (aggregated_PAS[how_time] <= end_measurement)]

    merged = pd.merge(
        aggregated_PAS, 
        aggregated_street, 
        how='left', 
        left_on=[how_time, how_space], 
        right_on=[how_time, how_space]
        ).copy()
    merged_out = pd.merge(
        merged, 
        aggregated_search, 
        how='left', 
        left_on=[how_time, how_space], 
        right_on=[how_time, how_space]
        ).copy()
    merged_out = merged_out.dropna().reset_index(drop=True).copy()

    return merged_out


def prepare_in_depth_PAS_categories(
        aggregated_street: pd.DataFrame, 
        aggregated_search: pd.DataFrame, 
        PAS: pd.DataFrame, 
        PAS_column_names: List[str], 
        how_time: str = "Month", 
        how_space: str = "Ward name") -> pd.DataFrame:
    """
    Prepares data for in depth analysis.
    """
    aggr_mapper = {}
    df = further_clean_PAS(PAS, recode=False).copy()

    for column in PAS_column_names:
        renamer = {}
        one_hot_encoded = pd.get_dummies(df[column])
        one_hot_encoded = one_hot_encoded.astype(int)
        df = pd.concat([df, one_hot_encoded], axis=1)
        for i in one_hot_encoded.columns:
            renamer[i] = f"{column}_{i}"
            aggr_mapper[renamer[i]] = ['sum']
        df = df.rename(columns=renamer).copy()

    for q in [
        'qLivedInAreaForYears',
        'qWorriedAboutCrimeInArea',
        'qGoodJobLocal',
        'qGoodJobLondon',
        'qReliedOnToBeThere',
        'qTreatEveryoneFairly',
        'qDealWithWhatMattersToTheCommunity',
        'qListenToConcerns',
        'qConfidentThatStopAndSearchFair',
        'qInformedLocal',
        'qInformedLondon',
        'Trust',
        'qPoliceHeldAccountable',
        ]:
        aggr_mapper[q] = ['mean']

    aggr_mapper['Year'] = ['first']
    aggr_mapper['Borough name'] = ['first']

    # Recoding
    question_mappers_dct = {}

    question_mappers_dct['qLivedInAreaForYears'] = {
        '5 years but less than 10 years': 7.5,
        '30 years or more': 35,
        '2 years but less than 3 years': 2.5,
        '12 months but less than 2 years': 1.5,
        'Less than 12 months': 0.5,
        '20 years but less than 30 years': 25,
        '3 years but less than 5 years': 4,
        '10 years but less than 20 years':15
    }
    question_mappers_dct['qWorriedAboutCrimeInArea'] = {
        'Not very worried': 2,
        'Fairly worried': 3,
        'Not at all worried': 1,
        'Very worried': 4,
    }
    for q in ['qGoodJobLocal', 'qGoodJobLondon']:
        question_mappers_dct[q] = {
            'Good': 4,
            'Excellent': 5,
            'Fair': 3,
            'Very poor': 1, 
            'Poor': 2,
        }
    
    for q in ['qReliedOnToBeThere', 'qTreatEveryoneFairly', 'qDealWithWhatMattersToTheCommunity', 'qListenToConcerns', 'Trust']:
        question_mappers_dct[q] = {
            'Tend to agree': 4,
            'Strongly agree': 5,
            'Tend to disagree': 2,
            'Neither agree nor disagree': 3,
            'Strongly disagree': 1
        }
    
    question_mappers_dct['qPoliceHeldAccountable'] = {
        'Tend to agree': 4,
        'Strongly agree': 5,
        'Tend to disagree': 2,
        'Neither agree nor disagree': 3,
        'Strongly disagree': 1,
        'Not Asked': np.nan,
        "Don't know": np.nan,
        'Refused': np.nan
        }
    
    question_mappers_dct['qConfidentThatStopAndSearchFair'] = {
        'Fairly confident':3,
        'Very confident': 4,
        'Not very confident': 2,
        'Not at all confident': 1,
    }

    for q in ['qInformedLocal', 'qInformedLondon']:
        question_mappers_dct[q] = {
        'Fairly well informed': 2, 
        'Not at all informed': 1, 
        'Very well informed': 3,
        }

    for column in question_mappers_dct:
        df[column] = df[column].map(question_mappers_dct[column])
    
    for q in ['qLivedInAreaForYears',
        'qWorriedAboutCrimeInArea',
        'qGoodJobLocal',
        'qGoodJobLondon',
        'qReliedOnToBeThere',
        'qTreatEveryoneFairly',
        'qDealWithWhatMattersToTheCommunity',
        'qListenToConcerns',
        'qConfidentThatStopAndSearchFair',
        'qInformedLocal',
        'qInformedLondon',
        'Trust',
        'qPoliceHeldAccountable']:
        df[q] = df[["Ward name", q]].groupby("Ward name").transform(lambda x: x.fillna(x.mean()))

    # Defining confidence
    weights = {
        'qGoodJobLocal': 0.2,
        'qTreatEveryoneFairly': 0.2,
        'qGoodJobLondon': 0.1,
        'qReliedOnToBeThere': 0.1,
        'qDealWithWhatMattersToTheCommunity': 0.1,
        'qListenToConcerns': 0.1,
        'qPoliceHeldAccountable': 0.1,
        'qInformedLocal': 0.05,
        'qInformedLondon': 0.05
    }

    def calculate_confidence(row): # Taken from Nabil's code
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
    aggr_mapper['Confidence'] = ['mean']
    df4 = df.groupby(['Month', "Ward name"]).agg(aggr_mapper).reset_index()
    df4.columns = [col_name[0] for col_name in df4.columns]
    

    out = join_data(aggregated_street, aggregated_search, df4, how_time, how_space, recode_to_period_PAS=False)

    return out





# aggregated_PAS = pd.read_csv('PAS_month_ward.csv')
street = pd.read_csv('street_month_ward.csv')
search = pd.read_csv('search_month_ward.csv')

# x = join_data(street, search, aggregated_PAS, how_space="Ward name", how_time="Month").drop(columns = ['Unnamed: 0_x'])
# x.to_csv('aggregation_attempt.csv')

PAS = pd.read_csv('PAS_new.csv')

prepare_in_depth_PAS_categories(street, search, PAS, ["qTreatEveryoneFairly", 
                                                      "qGoodJobLondon", 
                                                      "qPoliceHeldAccountable",
                                                      "qReliedOnToBeThere",
                                                      "qConfidentThatStopAndSearchFair"]).to_csv('experiment.csv')
