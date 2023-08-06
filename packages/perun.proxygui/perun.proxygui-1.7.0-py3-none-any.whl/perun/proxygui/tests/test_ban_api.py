import copy
import io
import json
import tarfile
import gzip
from unittest.mock import patch
from http import HTTPStatus

import mongomock
import pytest

from perun.proxygui.app import get_flask_app, get_config
from perun.proxygui.tests.shared_test_data import SHARED_TESTING_CONFIG, ATTRS_MAP

BAN_IN_DB_1 = {
    "description": None,
    "facilityId": "1",
    "id": 1,
    "userId": "57986",
    "validityTo": "1670799600000",
}

BAN_IN_DB_2 = {
    "description": "Something serious",
    "facilityId": "1",
    "id": 2,
    "userId": "54321",
    "validityTo": "1670799600000",
}

BAN_NOT_IN_DB_1 = {
    "description": None,
    "facilityId": "1",
    "id": 3,
    "userId": "12345",
    "validityTo": "1670799600000",
}

BAN_NOT_IN_DB_2 = {
    "description": "Something serious again",
    "facilityId": "1",
    "id": 4,
    "userId": "5678",
    "validityTo": "1670799600000",
}

MOCK_CLIENT = mongomock.MongoClient()
BAN_COLLECTION = MOCK_CLIENT["ban_database"]["ban_collection"]
BANS_IN_DB = [BAN_IN_DB_1, BAN_IN_DB_2]
BANS_NOT_IN_DB = [BAN_NOT_IN_DB_1, BAN_NOT_IN_DB_2]

for ban in BANS_IN_DB:
    BAN_COLLECTION.insert_one(copy.deepcopy(ban))

BANNED_SUBJECT = "banned_subject"
ALLOWED_SUBJECT = "allowed_subject"
SSP_SESSIONS_COLLECTION = MOCK_CLIENT["ssp_database"]["ssp_collection"]
SSP_SESSIONS = [
    {"user": BANNED_SUBJECT, "session_data": "1"},
    {"user": BANNED_SUBJECT, "session_data": "2"},
    {"user": ALLOWED_SUBJECT, "session_data": "1"},
    {"user": ALLOWED_SUBJECT, "session_data": "2"},
]

SATOSA_SESSIONS_COLLECTION = MOCK_CLIENT["satosa_database"]["ssp_collection"]
SATOSA_SESSIONS = [
    {"sub": BANNED_SUBJECT, "session_data": "1"},
    {"sub": BANNED_SUBJECT, "session_data": "2"},
    {"sub": ALLOWED_SUBJECT, "session_data": "1"},
    {"sub": ALLOWED_SUBJECT, "session_data": "2"},
]


@pytest.fixture()
def client():
    with patch(
        "perun.utils.ConfigStore.ConfigStore.get_global_cfg",
        return_value=SHARED_TESTING_CONFIG,
    ), patch(
        "perun.utils.ConfigStore.ConfigStore.get_attributes_map",
        return_value=ATTRS_MAP,
    ):
        cfg = get_config()
        app = get_flask_app(cfg)
        app.config["TESTING"] = True
        yield app.test_client()


@patch("perun.proxygui.api.ban_api.get_ban_collection")
def test_find_ban_ban_exists(mock_get_ban_collection, client):
    mock_get_ban_collection.return_value = BAN_COLLECTION

    response = client.get(f"/ban/{BAN_IN_DB_1['id']}")
    result = json.loads(response.data.decode())

    for key, value in BAN_IN_DB_1.items():
        assert result.get(key) == value


@patch("perun.proxygui.api.ban_api.get_ban_collection")
def test_find_ban_ban_doesnt_exist(mock_get_ban_collection, client):
    mock_get_ban_collection.return_value = BAN_COLLECTION

    not_in_db_ban_id = -1
    assert BAN_COLLECTION.find_one({"id": not_in_db_ban_id}) is None

    response = client.get(f"/ban/{not_in_db_ban_id}")
    result = json.loads(response.data.decode())

    assert result == {}


@patch("perun.proxygui.api.ban_api.get_ban_collection")
@patch("perun.connector.AdaptersManager.get_user_attributes")
def test_ban_user_all_users_already_banned(
    mock_get_user_attributes, mock_get_ban_collection, client
):
    mock_get_user_attributes.return_value = {
        SHARED_TESTING_CONFIG["perun_person_principal_names_attribute"]: BANNED_SUBJECT
    }
    mock_get_ban_collection.return_value = BAN_COLLECTION

    user_bans_in_db = {ban["userId"]: ban for ban in BANS_IN_DB}
    number_of_bans_in_db = len(BANS_IN_DB)

    assert BAN_COLLECTION.count_documents({}) == number_of_bans_in_db

    client.put("/banned-users/", data=user_bans_in_db)

    assert BAN_COLLECTION.count_documents({}) == number_of_bans_in_db


@patch("perun.proxygui.api.ban_api.delete_mitre_tokens")
@patch("perun.proxygui.api.ban_api.get_ban_collection")
@patch("perun.proxygui.api.ban_api.get_satosa_sessions_collection")
@patch("perun.proxygui.api.ban_api.get_ssp_sessions_collection")
@patch("perun.connector.AdaptersManager.get_user_attributes")
def test_ban_user_add_new_bans(
    mock_get_user_attributes,
    mock_get_ssp_collection,
    mock_get_satosa_collection,
    mock_get_ban_collection,
    mock_delete_mitre_tokens,
    client,
):
    mock_delete_mitre_tokens.return_value = 0
    mock_get_user_attributes.return_value = {
        SHARED_TESTING_CONFIG["perun_person_principal_names_attribute"]: BANNED_SUBJECT
    }
    mock_get_ssp_collection.return_value = SSP_SESSIONS_COLLECTION
    mock_get_satosa_collection.return_value = SATOSA_SESSIONS_COLLECTION
    mock_get_ban_collection.return_value = BAN_COLLECTION

    all_user_bans = {ban["userId"]: ban for ban in BANS_IN_DB + BANS_NOT_IN_DB}
    number_of_bans_in_db = len(BANS_IN_DB)
    number_of_bans_not_in_db = len(BANS_NOT_IN_DB)

    assert BAN_COLLECTION.count_documents({}) == number_of_bans_in_db

    client.put("/banned-users/", json=all_user_bans)

    assert (
        BAN_COLLECTION.count_documents({})
        == number_of_bans_in_db + number_of_bans_not_in_db
    )
    for ban in BANS_IN_DB + BANS_NOT_IN_DB:
        assert BAN_COLLECTION.find_one({"id": ban["id"]}) is not None

    assert SSP_SESSIONS_COLLECTION.count_documents(
        {}
    ) == SSP_SESSIONS_COLLECTION.count_documents({"user": ALLOWED_SUBJECT})
    assert SSP_SESSIONS_COLLECTION.find_one({"user": BANNED_SUBJECT}) is None

    assert SATOSA_SESSIONS_COLLECTION.count_documents(
        {}
    ) == SATOSA_SESSIONS_COLLECTION.count_documents({"sub": ALLOWED_SUBJECT})
    assert SATOSA_SESSIONS_COLLECTION.find_one({"sub": BANNED_SUBJECT}) is None


def test_ban_users_tar_missing_file(
    client,
):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w|gz") as tar:
        text = b"facility file content"
        file_data = io.BytesIO(text)
        info = tarfile.TarInfo(name="FACILITY")
        info.size = len(text)
        tar.addfile(info, file_data)
    tar.name = "sent_data"

    buffer.seek(0)
    gzipped_data = gzip.compress(buffer.read())

    response = client.put(
        "/banned-users-generic/", content_type="application/x-tar", data=gzipped_data
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@patch("perun.proxygui.api.ban_api.get_ban_collection")
def test_ban_users_tar_update(
    mock_get_ban_collection,
    client,
):
    mock_get_ban_collection.return_value = BAN_COLLECTION
    new_bans = {BAN_NOT_IN_DB_1["userId"]: BAN_NOT_IN_DB_1}

    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w|gz") as tar:
        text = json.dumps(new_bans).encode("utf-8")
        file_data = io.BytesIO(text)
        info = tarfile.TarInfo(name="./banned_facility_users")
        info.size = len(text)
        tar.addfile(info, file_data)
    tar.name = "data"

    buffer.seek(0)
    gzipped_data = gzip.compress(buffer.read())

    client.put(
        "/banned-users-generic/", content_type="application/x-tar", data=gzipped_data
    )

    assert BAN_COLLECTION.count_documents({}) == 1
