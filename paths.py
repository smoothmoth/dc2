import pandas as pd


def get_path_to_data(user: str, data: str) -> str:
    """
    Returns the path to data of a given person
    :param user: name of the person working with the data
    :param data: data to be accessed (PAS, stopandsearch, street, outcomes, or all)
    :return: path to data for a given user
    """
    path_dct = {
        "PAS": '/PAS_T&Cdashboard_to Q3 23-24.xlsx',
        "stopandsearch": "/metropolitan-stop-and-search.csv",
        "street":"/metropolitan-street-combined.csv",
        "outcomes":"/metropolitan-outcomes.csv",
        "all": ""
                }
    if user == 'Kuba':
        return "D:/DC2_Output"+path_dct[data]
    elif user == 'Nabil':
        return "DC2_data"+path_dct[data]
        # TODO everyone should add their path to data :)


# PAS_path = get_path_to_data('Kuba') + '/PAS_T&Cdashboard_to Q3 23-24.xlsx'
# PAS_csv = pd.read_csv(r"D:/DC2_data/PAS_T&Cdashboard_to Q3 23-24.xlsx")
#
# PAS_path_N = get_path_to_data('Nabil') + '/PAS_T&Cdashboard_to Q3 23-24.xlsx'
# PAS_excel_N = pd.read_excel('DC2_data/PAS_T&Cdashboard_to Q3 23-24.xlsx', sheet_name='Borough')