import sys
sys.path.append('../../')

import pandas as pd
from ml_models.clustering import get_geo_clusters

df = pd.read_csv('../../data/VNP14IMGTDL_NRT_Global_24h.csv')
fire_spots = get_geo_clusters(df, min_samples=40, eps=1.0)
print(fire_spots.head(10))