import json
from unittest.mock import patch

import pytest

from perun.proxygui.app import get_flask_app, get_config
from perun.proxygui.tests.shared_test_data import SHARED_TESTING_CONFIG


@pytest.fixture()
def client():
    with patch(
        "perun.utils.ConfigStore.ConfigStore.get_global_cfg",
        return_value=SHARED_TESTING_CONFIG,
    ), patch(
        "perun.utils.ConfigStore.ConfigStore.get_attributes_map",
        return_value=SHARED_TESTING_CONFIG,
    ):
        cfg = get_config()
        app = get_flask_app(cfg)
        app.config["TESTING"] = True
        yield app.test_client()


def test_is_testing_sp(client):
    response = client.get("/IsTestingSP")
    is_testing_sp_text = (
        "You are about to access service, which is in testing environment."
        # noqa
    )
    is_testing_sp_text_2 = "Continue"

    result = response.data.decode()
    assert is_testing_sp_text in result
    assert is_testing_sp_text_2 in result
    assert response.status_code == 200


def test_authorization_error(client):
    response = client.get("/authorization")

    assert response.status_code == 404


@patch("perun.proxygui.gui.gui.verify_jwt")
def test_authorization(mock_method, client):
    test_data = {
        "email": "email",
        "service": "service",
        "registration_url": "url",
    }

    test_result = json.dumps(test_data)
    is_testing_sp_text = "Access forbidden"
    is_testing_sp_text_2 = (
        "You don't meet the prerequisites for accessing the service: "  # noqa
    )
    is_testing_sp_text_3 = (
        "For more information about this service please visit this "  # noqa
    )
    is_testing_sp_text_4 = (
        "If you think you should have an access contact service operator at "
        # noqa
    )
    is_testing_sp_text_5 = "Problem with login to service: "
    mock_method.return_value = test_result
    response = client.get("/authorization/example")

    result = response.data.decode()
    assert is_testing_sp_text in result
    assert is_testing_sp_text_2 in result
    assert is_testing_sp_text_3 in result
    assert is_testing_sp_text_4 in result
    assert is_testing_sp_text_5 in result
    assert response.status_code == 200


def test_sp_authorization_error(client):
    response = client.get("/SPAuthorization")

    assert response.status_code == 404


@patch("perun.proxygui.gui.gui.verify_jwt")
def test_sp_authorization(mock_method, client):
    test_data = {
        "email": "mail",
        "service": "service",
        "registration_url": "url",
    }
    test_result = json.dumps(test_data)
    is_testing_sp_text = "You are not authorized to access the service "
    is_testing_sp_text_2 = (
        "We will now redirect you to a registration page, "
        + "where you will apply for the access."
    )
    is_testing_sp_text_3 = "Proceed to registration"
    mock_method.return_value = test_result
    response = client.get("/SPAuthorization/example")

    result = response.data.decode()
    assert is_testing_sp_text in result
    assert is_testing_sp_text_2 in result
    assert is_testing_sp_text_3 in result
    assert response.status_code == 200
