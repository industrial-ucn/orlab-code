import os.path
from collections import namedtuple

import numpy as np
import pandas as pd
import requests

Location = namedtuple('Location', 'id lat lon')

data_path = 'osrm.csv'


def osrm_time_row(locations):
    assert len(locations) <= 8_000, "Limit over maximum allowed."
    assert len(locations) >= 2, "More than one location is needed."
    str_locations = ';'.join(['%0.6f,%0.6f' % (loc.lon, loc.lat) for loc in locations])
    r = requests.get('http://localhost:5000/table/v1/driving/' + str_locations + '?sources=0')
    return r.json()['durations'][0][1:]


def osrm_time_matrix_batch_query(location_pair_list, query_limit=7):
    assert query_limit <= 8_000, "Limit over maximum allowed."
    assert query_limit >= 1, "Limit must be positive."
    assert query_limit == int(query_limit), " Limit must be integer."
    assert len(location_pair_list) > 0, "Not enough requests."
    location_pair_list = sorted(location_pair_list)
    origin = location_pair_list[0][0]
    destinations = []
    for k, (loc1, loc2) in enumerate(location_pair_list):
        # check if origin changed
        if origin != loc1:
            res = osrm_time_row([origin] + destinations)
            save_response(origin, destinations, res)
            origin = loc1
            destinations = [loc2]
        else:
            destinations.append(loc2)
        # check if the query limit is reached or end of location pair list
        if len(destinations) == query_limit or k + 1 == len(location_pair_list):
            res = osrm_time_row([origin] + destinations)
            save_response(origin, destinations, res)
            destinations = []
    return None


def save_response(origin, destinations, response):
    n = len(destinations)
    i_list = [origin.id for _ in range(n)]
    j_list = [destination.id for destination in destinations]
    df = pd.DataFrame({'i': i_list, 'j': j_list, 'response': response})
    with open(data_path, 'a') as f:
        df.to_csv(f, header=False, index=False)
    return None


def osrm_time_matrix(location_pair_list):
    if not os.path.isfile(data_path):
        osrm_time_matrix_batch_query(location_pair_list)
    else:
        df1 = pd.DataFrame({'i': [i.id for i, _ in location_pair_list],
                            'j': [j.id for _, j in location_pair_list]})
        df2 = pd.read_csv(data_path, header=None, usecols=[0, 1], names=['i', 'j'],
                          dtype={'i': np.int32, 'j': np.int32})
        df_all = df1.merge(df2.drop_duplicates(), on=['i', 'j'], how='left', indicator=True)
        df_empties = df_all[df_all['_merge'] == 'left_only']
        locations = {}
        for l1, l2 in location_pair_list:
            locations[l1.id] = l1
            locations[l2.id] = l2
        new_location_pair_list = []
        for k, row in df_empties.iterrows():
            new_location_pair_list.append((locations[row.i], locations[row.j]))
        osrm_time_matrix_batch_query(new_location_pair_list)
    return None
