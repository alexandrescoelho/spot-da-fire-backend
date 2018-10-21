from firebase_admin import db

DEFAULT_INSERT_PATH = "{0}"
DEFAULT_UPDATE_PATH = "{0}/{1}"
DEFAULT_DELETE_PATH = "{0}/{1}"
DEFAULT_GET_PATH = "{0}/{1}"
DEFAULT_GET_COLLECTION_PATH = "{0}"

class BaseRepository:
    def __init__(self, database_name):
        self._database_name = database_name

    def reset(self, value):
        database_ref = db.reference(DEFAULT_INSERT_PATH.format(self._database_name))
        try:
            ref = database_ref.set(value)
            #value["id"] = ref._segments
            #return value
        except Exception as insert_exception:
            raise insert_exception

    def add(self, value):
        database_ref = db.reference(DEFAULT_INSERT_PATH.format(self._database_name))
        try:
            ref = database_ref.push()
            value["id"] = ref.key
            ref.set(value)
            return value
        except Exception as insert_exception:
            raise insert_exception

    def update(self, id, value):
        database_ref = db.reference(DEFAULT_UPDATE_PATH.format(self._database_name, id))
        try:
            ref = database_ref.update(value)
            return value
        except Exception as update_exception:
            raise update_exception

    def get(self, id):
        database_ref = db.reference(DEFAULT_GET_PATH.format(self._database_name, id))
        value = database_ref.get()
        return value

    def get_collection(self):
        database_ref = db.reference(DEFAULT_GET_COLLECTION_PATH.format(self._database_name))
        values = database_ref.get()
        return values

    def delete(self, id):
        database_ref = db.reference(DEFAULT_DELETE_PATH.format(self._database_name, id))
        try:
            database_ref.delete()
        except Exception as update_exception:
            raise update_exception