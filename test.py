import pandas as pd
from geopy.distance import great_circle

from orlabucn import osrm
from orlabucn.osrm import Location, osrm_time_matrix

df = pd.read_excel('Puntos_medios.xlsx')
ref_lat, ref_lon = df.Lat.min(), df.Lon.min()
locations = []
for i, row in df.iterrows():
    x = great_circle((ref_lat, ref_lon), (ref_lat, row.Lon)).meters
    y = great_circle((ref_lat, ref_lon), (row.Lat, ref_lon)).meters
    new_location = Location(id=int(row.Id), lat=row.Lat, lon=row.Lon, x=x, y=y)
    locations.append(new_location)

pairs = [(l1, l2) for l1 in locations for l2 in locations
         if l1 != l2 and abs(l1.x - l2.x) <= 1_000 and abs(l1.y - l2.y) <= 1_000]

print(len(locations) * (len(locations) - 1), "->", len(pairs))

osrm.data_path = 'osrm5.csv'

osrm_time_matrix(pairs)
