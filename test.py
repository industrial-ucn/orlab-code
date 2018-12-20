import pandas as pd

from orlabucn.osrm import Location, osrm_time_matrix

df = pd.read_excel('Coordinates.xlsx')

locations = []
for i, row in df.iterrows():
    new_location = Location(id=int(row.ID), lat=row.Lat, lon=row.Long)
    locations.append(new_location)
    if len(locations) > 10:
        break

osrm_time_matrix([(l1, l2) for l1 in locations for l2 in locations if l1 != l2])
