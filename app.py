import json
import logging
from flask import Flask, request
import firebase_admin
from firebase_admin import credentials

from repositories.spoted_fire_repository import SpotedFireRepository
from repositories.brightness_clustering_repository import BrightnessClusteringRepository
from repositories.density_clustering_repository import DensityClusteringRepository

from util import csvtolist

from ml_models.clustering import get_brightness_clusters
from ml_models.clustering import get_geo_clusters

from GeoFire.geofire import GeoFire
import pygeohash as geohash

app = Flask(__name__)

cred = credentials.Certificate('./credentials.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://nasa-hackathon-team-1.firebaseio.com/'
})


@app.route('/')
def hello_world():
    return "It's alive!"


@app.route('/fire/api/v1.0/refresh-nasa-data', methods=['GET'])
def refresh_nasa_data():
    res_code = 201
    try:
        fires = csvtolist.get_list()
        print('last 24h registers %s', fires.__len__())
        app.logger.info('last 24h registers %d', fires.__len__())
        fire_repo = SpotedFireRepository()
        fire_repo.reset(fires)
        print('saved %d to db', fires.__len__())
    except Exception as load_data:
        print('something went wrong: %s', load_data)
        res_code = 500
    return '', res_code


@app.route('/fire/api/v1.0', methods=['GET'])
def get_fire_collection():
    try:
        lat = request.args.get('lat', default=-5.37895, type=float)
        lon = request.args.get('lon', default=11.44103, type=float)

        logging.info("lat:{} lon:{}".format(lat, lon))
        print("lat:{} lon:{}".format(lat, lon))

        geofire = GeoFire(lat=lat,
                          lon=lon,
                          radius=50,
                          unit='km').config_firebase(cred,
                                                     auth_domain='nasa-hackathon-team-1.firebaseapp.com',
                                                     database_URL='https://nasa-hackathon-team-1.firebaseio.com/',
                                                     storage_bucket='nasa-hackathon-team-1.appspot.com')

        nearby_fire = geofire.query_nearby_objects(query_ref='spoted-fire',
                                                             geohash_ref='geohash')

        return json.dumps(nearby_fire)

    except Exception as get_collection:
        logging.error('something went wrong', get_collection)
        return '', 500


# BRIGHTNESS CLUSTERING ENDPOINTS
@app.route('/fire/api/v1.0/fetch-brightness-clusters', methods=['GET'])
def fetch_brightness_clusters():
    try:
        lat = request.args.get('lat', default=-5.37895, type=float)
        lon = request.args.get('lon', default=11.44103, type=float)

        geofire = GeoFire(lat=lat,
                          lon=lon,
                          radius=50,
                          unit='km').config_firebase(cred,
                                                     auth_domain='nasa-hackathon-team-1.firebaseapp.com',
                                                     database_URL='https://nasa-hackathon-team-1.firebaseio.com/',
                                                     storage_bucket='nasa-hackathon-team-1.appspot.com')

        nearby_brigthness_cluster = geofire.query_nearby_objects(query_ref='brightness-clustering',
                                                                 geohash_ref='geohash')
        return json.dumps(nearby_brigthness_cluster)

    except Exception as get_collection:
        logging.error('something went wrong', get_collection)
        return '', 500


@app.route('/fire/api/v1.0/refresh-brightness-cluster-data', methods=['GET'])
def create_save_cluster_data():
    dataset = csvtolist.get_24h_list()
    fire_spots = get_brightness_clusters(dataset)

    fire_spots['geohash'] = fire_spots.drop('cluster', axis=1).apply(lambda x: geohash.encode(x.latitude, x.longitude, precision=5), axis=1)

    fire_spots = fire_spots.to_dict(orient='row')

    fire_repo = BrightnessClusteringRepository()
    fire_repo.reset(fire_spots)

    return '', 201


# DENSITY CLUSTERING ENDPOINTS
@app.route('/fire/api/v1.0/fetch-density-clusters', methods=['GET'])
def fetch_density_clusters():
    try:
        lat = request.args.get('lat', default=-5.37895, type=float)
        lon = request.args.get('lon', default=11.44103, type=float)

        geofire = GeoFire(lat=lat,
                          lon=lon,
                          radius=50,
                          unit='km').config_firebase(cred,
                                                     auth_domain='nasa-hackathon-team-1.firebaseapp.com',
                                                     database_URL='https://nasa-hackathon-team-1.firebaseio.com/',
                                                     storage_bucket='nasa-hackathon-team-1.appspot.com')

        nearby_density_cluster = geofire.query_nearby_objects(query_ref='density-clustering',
                                                                 geohash_ref='geohash')
        return json.dumps(nearby_density_cluster)

    except Exception as get_collection:
        logging.error('something went wrong', get_collection)
        return '', 500


@app.route('/fire/api/v1.0/refresh-density-cluster-data', methods=['GET'])
def create_save_density_cluster_data():
    dataset = csvtolist.get_24h_list()
    fire_spots = get_geo_clusters(dataset, min_samples=40, eps=1.0)

    fire_spots['geohash'] = fire_spots.drop(['cluster', 'color'], axis=1).apply(lambda x: geohash.encode(x.latitude, x.longitude, precision=5), axis=1)

    fire_spots = fire_spots.to_dict(orient='row')

    fire_repo = DensityClusteringRepository()
    fire_repo.reset(fire_spots)

    return '', 201


if __name__ == '__main__':
    app.run()
