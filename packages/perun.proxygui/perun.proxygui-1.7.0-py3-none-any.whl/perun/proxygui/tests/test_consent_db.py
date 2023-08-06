import mongomock
from unittest import TestCase
from perun.utils.consent_framework.consent import Consent
from perun.utils.consent_framework.consent_db import ConsentDB
from datetime import datetime


class TestConsentDB(TestCase):
    def setUp(self):
        self.cfg = {
            "consent": {"months_valid": 6},
            "test_db": {
                "connection_string": "mongodb://localhost:27017/",
                "database_name": "test_db",
                "consent_collection_name": "test_collection",
            },
        }
        self.mock_client = mongomock.MongoClient()
        self.mock_collection = self.mock_client.test_db.test_collection
        self.consent_db = ConsentDB(self.cfg, "test_db")
        self.consent = Consent(
            {"test_attribute": "test_value"},
            "test_user_id",
            "test_requester",
            6,
            datetime.utcnow(),
        )

    def test_save_consent(self):
        self.consent_db.collection = self.mock_collection
        self.consent_db.save_consent("test_consent_id", self.consent)
        self.assertTrue(
            self.mock_collection.find_one({"consent_id": "test_consent_id"})
        )

    def test_get_consent(self):
        self.consent_db.collection = self.mock_collection
        self.consent_db.save_consent("test_consent_id", self.consent)
        result = self.consent_db.get_consent("test_consent_id")
        self.assertEqual(result.attributes, {"test_attribute": "test_value"})
        self.assertEqual(result.user_id, "test_user_id")
        self.assertEqual(result.requester, "test_requester")
        self.assertEqual(result.months_valid, 6)

    def test_delete_consent(self):
        self.consent_db.collection = self.mock_collection
        self.consent_db.save_consent("test_consent_id", self.consent)
        self.consent_db.delete_consent("test_consent_id")
        self.assertIsNone(
            self.mock_collection.find_one({"consent_id": "test_consent_id"})
        )

    def test_delete_user_consent(self):
        self.consent_db.collection = self.mock_collection
        self.consent_db.save_consent("test_consent_id1", self.consent)
        self.consent_db.save_consent("test_consent_id2", self.consent)
        self.consent_db.delete_user_consent("test_user_id")
        self.assertEqual(
            self.mock_collection.count_documents({"user_id": "test_user_id"}), 0
        )
