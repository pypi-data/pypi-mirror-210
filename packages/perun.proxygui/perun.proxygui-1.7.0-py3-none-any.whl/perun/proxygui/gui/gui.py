import copy
import json

from uuid import uuid4

import yaml
from flask import Blueprint
from flask import render_template, make_response, jsonify, session
from flask_babel import gettext


from perun.proxygui.jwt import verify_jwt
from perun.utils.consent_framework.consent_manager import ConsentManager


def ignore_claims(ignored_claims, claims):
    result = dict()

    for claim in claims:
        if claim not in ignored_claims:
            result[claim] = claims[claim]

    return result


def construct_gui_blueprint(cfg):
    gui = Blueprint("gui", __name__, template_folder="templates")
    consent_db_manager = ConsentManager(cfg)

    REDIRECT_URL = cfg["redirect_url"]
    COLOR = cfg["bootstrap_color"]

    KEY_ID = cfg["key_id"]
    KEYSTORE = cfg["keystore"]

    @gui.route("/authorization/<message>")
    def authorization(message):
        message = json.loads(verify_jwt(message, KEYSTORE, KEY_ID))
        email = message.get("email")
        service = message.get("service")
        registration_url = message.get("registration_url")
        if not email or not service:
            return make_response(
                jsonify({gettext("fail"): gettext("Missing request parameter")}),
                400,
            )  # noqa
        return render_template(
            "authorization.html",
            email=email,
            service=service,
            registration_url=registration_url,
            bootstrap_color=COLOR,
        )

    @gui.route("/SPAuthorization/<message>")
    def sp_authorization(message):
        message = json.loads(verify_jwt(message, KEYSTORE, KEY_ID))
        email = message.get("email")
        service = message.get("service")
        registration_url = message.get("registration_url")
        return render_template(
            "SPAuthorization.html",
            email=email,
            service=service,
            registration_url=registration_url,
            bootstrap_color=COLOR,
        )

    @gui.route("/IsTestingSP")
    def is_testing_sp():
        return render_template(
            "IsTestingSP.html",
            redirect_url=REDIRECT_URL,
            bootstrap_color=COLOR,
        )

    @gui.route("/consent/<ticket>")
    def consent(ticket):
        ticket = json.loads(verify_jwt(ticket, KEYSTORE, KEY_ID))
        data = consent_db_manager.fetch_consent_request(ticket)
        if not ticket:
            return make_response(
                jsonify({gettext("fail"): gettext("received invalid ticket")}),
                400,
            )

        months_valid = cfg["consent"]["months_valid"]
        session["id"] = data["id"]
        session["state"] = uuid4().urn
        session["redirect_endpoint"] = data["redirect_endpoint"]
        session["attr"] = ignore_claims(cfg["consent"]["ignored_claims"], data["attr"])
        session["user_id"] = data["user_id"]
        session["locked_attrs"] = data.get("locked_attrs")
        session["requester_name"] = data["requester_name"]
        session["month"] = months_valid

        warning = cfg["consent"].get("warning", None)
        with open(
            cfg["consent"]["attribute_config_path"],
            "r",
            encoding="utf8",
        ) as ymlfile:
            attr_config = yaml.safe_load(ymlfile)

        return render_template(
            "ConsentRegistration.html",
            bootstrap_color=COLOR,
            cfg=cfg,
            attr_config=attr_config,
            released_claims=copy.deepcopy(session["attr"]),
            locked_claims=session["locked_attrs"],
            requester_name=session["requester_name"],
            months=months_valid,
            data_protection_redirect=data["data_protection_redirect"],
            warning=warning,
        )

    return gui
