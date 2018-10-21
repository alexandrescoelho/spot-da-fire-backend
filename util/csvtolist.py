import pygeohash as geohash
import requests
import pandas as pd
import io

NASA_ENDPOINT = 'https://firms.modaps.eosdis.nasa.gov/data/active_fire/viirs/csv/VNP14IMGTDL_NRT_Global_7d.csv'

def get_list():
    # read the csv file from nasa
    req = requests.get(NASA_ENDPOINT)
    data = io.StringIO(req.text)
    df = pd.read_csv(data)
    df['geohash'] = df.apply(lambda x: geohash.encode(x.latitude, x.longitude, precision=5), axis=1)

    records = df.to_dict(orient='row')
    return records
