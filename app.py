import json
import logging
from flask import Flask, request
import firebase_admin
from firebase_admin import credentials

from repositories.spoted_fire_repository import SpotedFireRepository
from util import csvtolist

from GeoFire.geofire import GeoFire

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
        fire_repo.reset(fires[:1000])
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


if __name__ == '__main__':
    app.run()
