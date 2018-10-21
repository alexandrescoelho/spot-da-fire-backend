import sys
sys.path.append('../../')

import pandas as pd
from ml_models.clustering import get_brightness_clusters

df = pd.read_csv('../../data/VNP14IMGTDL_NRT_Global_24h.csv')
fire_spots = get_brightness_clusters(df)
print(fire_spots.head(10))