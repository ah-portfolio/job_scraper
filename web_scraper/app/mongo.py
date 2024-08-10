import pymongo
import logging

from app.config import Settings

config = Settings()

log = logging.getLogger(__name__)

class Database:
    def __init__(self, collection: str):
        self.collection = collection

    def insert(self, datas:dict):
        client = pymongo.MongoClient(config.mongo_hostname,config.mongo_port)
        db = client[config.mongo_db]
        target_collection = db[self.collection]
        mongo_insertion_id = []
        for data in datas.values():
            try:
                x = target_collection.insert_one(data)
                mongo_insertion_id.append(x.inserted_id)
            except Exception as e:
                log.error(f"Unsuccessfull load in database of : {data} because of {e}")
                pass
        client.close()
        log.info(f"Successfull insert into db: {mongo_insertion_id} ")

    def select_by_session_id(self, session_id: str):
        client = pymongo.MongoClient(config.mongo_hostname,config.mongo_port)
        db = client[config.mongo_db]
        collection = db[self.collection]
        query = {"session_id": session_id}
        projection = {"_id": 0, "session_id":0}
        documents = collection.find(query, projection)
        returned_document = list(documents)  
        client.close()
        return returned_document       
