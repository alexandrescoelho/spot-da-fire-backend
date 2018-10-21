import datetime

from repositories.base_repository import BaseRepository, DEFAULT_GET_COLLECTION_PATH, DEFAULT_INSERT_PATH
from firebase_admin import db

class SpotedFireRepository(BaseRepository):
    def __init__(self):
        super().__init__("spoted-fire")

    def get_collection(self):
        curr_date = datetime.datetime.now()
        curr_date_str = '{}-{}-{}'.format(curr_date.strftime("%Y"), curr_date.strftime("%m"), curr_date.strftime("%d"))
        database_ref = db.reference(DEFAULT_INSERT_PATH.format(self._database_name))
        values = database_ref.order_by_child('acq_date').equal_to(curr_date_str)  #this one works

        return values.get()
#firebase.database().ref(`/rooms/$roomKey/messages`).orderByChild('createdAt').startAt('15039996197').on(//code);
