import pandas as pd
import police_api
from police_api import PoliceAPI
from typing import List

api = PoliceAPI()


def get_MPS() -> police_api.Force:
    """
    Access the Metropolitan Police Service Force object
    :return: Force object of MPS
    """
    return api.get_forces()[24]


def get_MPS_neighbourhoods() -> List[police_api.Neighbourhood]:
    """
    Returns Neighbourhoods associated with MPS.
    :return: A List of Neighbourhoods associated with MPS.
    """
    MPS = get_MPS()
    return api.get_neighbourhoods(MPS)


def locate_all_neighbourhoods(longitude_latitude: pd.DataFrame) -> pd.DataFrame:
    """
    Augments the data with two rows: neighbourhood.id; neighbourhood.name per id/ name. :param longitude_latitude: a
    dataframe with two Series: latitude and longitude :return: a dataframe with two rows: one with ID's of
    neighbourhoods extracted from the positional data; the other with names of corresponding neighbourhoods
    """
    neigh_id = []
    neigh_nm = []
    for row in longitude_latitude.rows:
        if row[1] is not None and row[0] is not None:
            neigh_id.append(api.locate_neighbourhood(row[1], row[0]).id)
            neigh_nm.append(api.locate_neighbourhood(row[1], row[0]).nm)
        else:
            neigh_id.append(None)
            neigh_nm.append(None)
    return pd.DataFrame({"neighbourhood_id": neigh_id, "neighbourhood_name": neigh_nm})


print(api.locate_neighbourhood(51.842619, -0.936784).id) # this is how you locate a nmeighbourhood based on coordinates (!)
print(len(get_MPS_neighbourhoods()))  # 679 neighbourhoods for MPS
nbhs = get_MPS_neighbourhoods()
# for nbh in nbhs:
#     print("++++++")
#     print(nbh.name)
#     for event in nbh.events:
#         print(event)
#         print(event.start_date)
#         print("----------")

# for nbh in nbhs:
#     print("++++++")
#     print(nbh.name)
#     print(nbh.officers)

for nbh in nbhs:
    print("++++++")
    print(nbh.name)
    for prio in nbh.priorities:
        print(prio)
        print(prio.issue_date)
        print("----------")