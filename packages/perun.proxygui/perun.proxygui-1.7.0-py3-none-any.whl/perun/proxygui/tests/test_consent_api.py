from unittest.mock import patch
from http import HTTPStatus

import pytest

from perun.proxygui.app import get_flask_app, get_config
from perun.proxygui.tests.shared_test_data import SHARED_TESTING_CONFIG, ATTRS_MAP


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


def test_verify_endpoint(client):
    with patch(
        "perun.utils.consent_framework.consent_manager."
        "ConsentManager.fetch_consented_attributes",
        return_value={"attr1": "value1", "attr2": "value2"},
    ):
        response = client.get("/verify/consent_id")
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == {"attr1": "value1", "attr2": "value2"}

    with patch(
        "perun.utils.consent_framework.consent_manager."
        "ConsentManager.fetch_consented_attributes",
        return_value=None,
    ):
        response = client.get("/verify/consent_id")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_save_consent_endpoint(client):
    with client.session_transaction() as session:
        session["state"] = "state"
        session["attr"] = {"attr1": "value1", "attr2": "value2"}
        session["locked_attrs"] = []
        session["id"] = "id"
        session["user_id"] = "user_id"
        session["requester_name"] = "requester_name"
        session["redirect_endpoint"] = "/redirect"

    with patch(
        "perun.utils.consent_framework.consent_manager.ConsentManager.save_consent"
    ):
        response = client.get(
            "/save_consent?state=state&validation=true&consent_"
            "status=yes&month=6&attr1=value1&attr2=value2"
        )
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"] == "/redirect"

    with client.session_transaction() as session:
        session["state"] = "state"
        session["attr"] = {"attr1": "value1", "attr2": "value2"}
        session["locked_attrs"] = []
        session["id"] = "id"
        session["user_id"] = "user_id"
        session["requester_name"] = "requester_name"
        session["redirect_endpoint"] = "/redirect"

    with patch(
        "perun.utils.consent_framework.consent_manager.ConsentManager.save_consent"
    ):
        response = client.get(
            "/save_consent?state=invalid_state&validation=true&consent_"
            "status=yes&month=6&attr1=value1&attr2=value2"
        )
    assert response.status_code == HTTPStatus.FORBIDDEN

    with patch(
        "perun.utils.consent_framework.consent_manager.ConsentManager.save_consent"
    ):
        response = client.get(
            "/save_consent?state=state&validation=true&consent_status="
            "yes&month=6&attr1=value1&attr3=value3"
        )
    assert response.status_code == HTTPStatus.BAD_REQUEST
