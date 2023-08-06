import mongomock
import json
from unittest import TestCase
from datetime import datetime
from perun.utils.consent_framework.consent_request import ConsentRequest
from perun.utils.consent_framework.consent_request_db import ConsentRequestDB


class TestConsentRequestDB(TestCase):
    def setUp(self):
        self.cfg = {
            "consent": {"months_valid": 6},
            "test_db": {
                "connection_string": "mongodb://localhost:27017/",
                "database_name": "test_db",
                "ticket_collection_name": "test_collection",
            },
        }
        self.mock_client = mongomock.MongoClient()
        self.mock_db = self.mock_client["test_db"]
        self.mock_collection = self.mock_db["test_collection"]
        self.consent_request_db = ConsentRequestDB(self.cfg, "test_db")
        self.consent_request_db.collection = self.mock_collection
        self.timestamp = datetime.utcnow()
        self.consent_request = ConsentRequest(
            {
                "attr": {1: 1, 2: 2, 3: 3},
                "redirect_endpoint": "endpoint",
                "id": "test_id",
            },
            self.timestamp,
        )

    def test_save_consent_request(self):
        ticket = "abc123"
        self.consent_request_db.save_consent_request(ticket, self.consent_request)

        result = self.mock_collection.find_one({"ticket": ticket})
        self.assertEqual(result["attributes"], json.dumps(self.consent_request.data))

    def test_get_consent_request(self):
        ticket = "abc123"
        self.consent_request_db.save_consent_request(ticket, self.consent_request)

        result = self.consent_request_db.get_consent_request(ticket)
        self.assertIsInstance(result, ConsentRequest)
        self.assertEqual(json.dumps(result.data), json.dumps(self.consent_request.data))

    def test_delete_consent_request(self):
        ticket = "abc123"
        self.consent_request_db.save_consent_request(ticket, self.consent_request)

        self.consent_request_db.delete_consent_request(ticket)
        result = self.mock_collection.find_one({"ticket": ticket})
        self.assertIsNone(result)
