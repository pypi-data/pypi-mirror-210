import json

from typing import Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from perun.utils.consent_framework.consent import Consent


class ConsentDB:
    def __init__(self, cfg, cfg_db_name):
        self.months_valid = cfg["consent"]["months_valid"]
        self.collection = self.get_database(cfg, cfg_db_name)

    def get_consent(self, consent_id: str) -> Optional[Consent]:
        consent_dict = self.collection.find_one({"consent_id": consent_id})
        if not consent_dict:
            return

        consent = Consent(
            json.loads(consent_dict["attributes"]),
            consent_dict["user_id"],
            consent_dict["requester_name"],
            consent_dict["months_valid"],
            consent_dict["timestamp"],
        )
        if consent.has_expired(self.months_valid):
            self.delete_consent(consent_id)
            return

        return consent

    def delete_consent(self, consent_id: str):
        self.collection.delete_one({"consent_id": consent_id})

    def save_consent(self, consent_id: str, consent: Consent):
        data = {
            "consent_id": consent_id,
            "user_id": consent.user_id,
            "requester_name": consent.requester,
            "timestamp": consent.timestamp,
            "months_valid": consent.months_valid,
            "attributes": json.dumps(consent.attributes),
        }

        self.collection.insert_one(data)

    def delete_user_consent(self, user_id):
        self.collection.delete_many({"user_id": user_id})

    @staticmethod
    def get_database(cfg, cfg_db_name: str) -> Collection:
        client = MongoClient(cfg[cfg_db_name]["connection_string"])
        database_name = cfg[cfg_db_name]["database_name"]
        collection_name = cfg[cfg_db_name]["consent_collection_name"]

        return client[database_name][collection_name]
