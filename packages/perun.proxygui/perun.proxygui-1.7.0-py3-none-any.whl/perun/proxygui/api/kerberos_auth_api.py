import base64
import json
from http import HTTPStatus
from sys import platform

import flask
from perun.connector import Logger

from flask import Blueprint, request

logger = Logger.get_logger(__name__)


def construct_kerberos_auth_api_blueprint(cfg):
    kerberos_auth_api = Blueprint("kerberos_auth_api", __name__)

    @kerberos_auth_api.route("/AuthenticateKerberosTicket")
    def authenticate_kerberos_ticket():
        """
        Import done here to prevent other endpoints from being dependent on
        the kerberos
        module. Flask blueprints are assembled in one file and this process
        would automatically start
        importing kerberos modules regardless of their uselessnes for other
        endpoints.
        """
        if platform.lower().startswith("win"):
            import winkerberos as kerberos
        else:
            import kerberos

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            response = flask.Response("")
            response.status_code = HTTPStatus.UNAUTHORIZED
            response.headers["WWW-Authenticate"] = "Negotiate"
            return response

        # auth header should look like 'Negotiate <base64_string>'
        required_prefix = "Negotiate "
        if not auth_header.startswith(required_prefix):
            return (
                "Kerberos ticket in authorization header must start with "
                "'Negotiate'. Incorrect format was provided in "
                "authorization header.",
                HTTPStatus.BAD_REQUEST,
            )

        b64_client_token = auth_header.removeprefix(required_prefix)
        client_token = base64.b64decode(b64_client_token).decode()

        service_name = cfg["kerberos_service_name"]
        result, context = kerberos.authGSSServerInit(service_name)
        if result != kerberos.AUTH_GSS_COMPLETE:
            return (
                "Error initializing Kerberos server context",
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )

        result = kerberos.authGSSServerStep(context, client_token)
        logger.info("Result of Kerberos ticket authentication: ", json.dumps(result))
        if result == kerberos.AUTH_GSS_COMPLETE:
            return "Kerberos authentication successful", HTTPStatus.OK
        elif result == kerberos.AUTH_GSS_CONTINUE:
            challenge_token = kerberos.authGSSServerResponse(context)
            response = flask.Response("")
            response.headers[
                "WWW-Authenticate"
            ] = f"Negotiate {base64.b64encode(challenge_token).decode()}"
            response.status_code = HTTPStatus.UNAUTHORIZED

            return response
        else:
            return "Kerberos authentication failed", HTTPStatus.UNAUTHORIZED

    return kerberos_auth_api
