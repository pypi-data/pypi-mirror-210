from http import HTTPStatus
from unittest.mock import patch

import pytest

from perun.proxygui.app import get_config, get_flask_app
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


def test_auth_no_auth_header_sent(client):
    response = client.get("/AuthenticateKerberosTicket")

    no_auth_header_msg = "Negotiate"

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert no_auth_header_msg in response.headers.get("WWW-Authenticate")


def test_auth_invalid_format_auth_header(client):
    headers = {"Authorization": "Something wrong here"}
    response = client.get("/AuthenticateKerberosTicket", headers=headers)

    invalid_format_auth_header_msg = (
        "Kerberos ticket in authorization "
        "header must start with 'Negotiate'. "
        "Incorrect format was provided in "
        "authorization header."
    )  # noqa

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert invalid_format_auth_header_msg in response.text
