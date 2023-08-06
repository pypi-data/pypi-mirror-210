import json

from datetime import datetime
from typing import Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from perun.utils.consent_framework.consent_request import ConsentRequest


class ConsentRequestDB:
    def __init__(self, cfg, cfg_db_name):
        self.collection = self.get_database(cfg, cfg_db_name)

    def get_consent_request(self, ticket: str) -> Optional[ConsentRequest]:
        request_dict = self.collection.find_one({"ticket": ticket})

        if request_dict:
            return ConsentRequest(
                json.loads(request_dict["attributes"]), request_dict["timestamp"]
            )

    def delete_consent_request(self, ticket: str):
        self.collection.delete_one({"ticket": ticket})

    def save_consent_request(self, ticket: str, consent_request: ConsentRequest):
        data = {
            "ticket": ticket,
            "attributes": json.dumps(consent_request.data),
            "timestamp": datetime.utcnow(),
        }

        self.collection.insert_one(data)

    @staticmethod
    def get_database(cfg, cfg_db_name: str) -> Collection:
        client = MongoClient(cfg[cfg_db_name]["connection_string"])
        database_name = cfg[cfg_db_name]["database_name"]
        collection_name = cfg[cfg_db_name]["ticket_collection_name"]

        return client[database_name][collection_name]
