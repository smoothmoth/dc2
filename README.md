# dc2
Data Challenge 2 Group 13 Repository
Group members: Jakub Malinowski, Hetvi Chaniyara, Nabil Talih, Milou der Kinderen, Chenxiao Zhou

# Downloading Data

### PAS Data
1. For inititial PAS data go to: https://data.london.gov.uk/dataset/mopac-surveys, and download PAS_T&Cdashboard_toQ3 23-24.xlsx
2. For ward-level PAS data, consult the stakeholder (the data was given to us by you)

### Stop and Search data; Crime data
1. Go to https://data.police.uk/data/archive/
2. Download the following folders: February 2015, February 2018, February 2021, February 2024

### Pay per boroguh
1. Go to https://data.london.gov.uk/dataset/earnings-place-residence-borough
2. Download the earnings-residence-borough.xls 

### Jobs density per borough
1. Go to https://data.london.gov.uk/dataset/jobs-and-job-density-borough
2. Download the Jobs and Job Density file

### Ethnicity per borough
1. Go to https://data.london.gov.uk/dataset/ethnic-groups-borough
2. Download the ethnic-groups-by-borough.xls file

### Ward boundaries
1. Go to https://geoportal.statistics.gov.uk/datasets/ons::wards-dec-2020-uk-bgc-2/about
2. Click download.

### Borough boundaries
1. Go to https://github.com/utisz/compound-cities/blob/master/greater-london.geo.json
2. Dowload the file.

# Programs and libraries

## Python
Python version: 3.10

Libraries + versions:
- pandas               2.2.2
- matplotlib           3.8.4
- numpy                1.26.4
- geojson              3.1.0
- geopandas            0.14.4
- seaborn              0.13.2
- folium               0.17.0
## R
R version 4.4.0

Libraries + versions:
- plm 2.6.4
- lmtest 0.9.40      
- Hmisc 5.1.3       
- car 3.1.2              
- modelsummary 2.1.0 
- foreign 0.8.86    
- dplyr 1.1.4        
- lubridate 1.9.3


# Running the code

## Powershell
The file is split into 2 code sections that you need to run:
1. Code to Remove the files for the other police forces: the main folder is the folder with all the subfolders for each month. Make sure to change it for every mainfolder.
2. Code to Merge file: Add all main folder names to the list and the merged files get saved in your output folder.
        - Do not forget to specify the output folder and main folder name according to your directory

## Python
1. Run functions main_1, main_2 in data_preparation.py. Follow the instructions provided in the docstrings.
2. Move all the ward-level Python files to the main project directory
3. Run choose.py
4. Move files PAS_ward_level_FY_15_17_prep.csv, PAS_ward_level_FY_17_18_prep.csv, PAS_ward_level_FY_18_19_prep.csv, PAS_ward_level_FY_19_20_prep.csv to the combine_csv folder
5. Run combine.py 
6. Run main_3, main_4,prepare_data_for_logistic_regression. Follow the instructions provided in the docstrings.
7. For EDA, follow the instructions in the files in the folder EDA. In case of problems with paths, ensure that you changed the paths accordingly and that the file that you need to use is in the EDA folder.



## R
1. Run analysis_final.R for all statistical tests and analysis results.
2. For logistic regression model F1 run Stop-Randomeness.ipynb
