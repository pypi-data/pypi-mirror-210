import json

from perun.connector import Logger
from perun.proxygui.jwt import verify_jwt
from flask import Blueprint, request, jsonify, abort, session, redirect
from perun.utils.consent_framework.consent_manager import (
    ConsentManager,
    InvalidConsentRequestError,
)
from perun.utils.consent_framework.consent import Consent

logger = Logger.get_logger(__name__)


def construct_consent_api(cfg):
    consent_api = Blueprint("consent_framework", __name__)
    db_manager = ConsentManager(cfg)

    KEY_ID = cfg["key_id"]
    KEYSTORE = cfg["keystore"]

    @consent_api.route("/verify/<consent_id>")
    def verify(consent_id):
        attrs = db_manager.fetch_consented_attributes(consent_id)
        if attrs:
            return jsonify(attrs)

        logger.debug("no consent found for id '%s'", consent_id)
        abort(401)

    @consent_api.route("/creq/<jwt>", methods=["GET", "POST"])
    def creq(jwt):
        if request.method == "POST":
            jwt = request.values.get("jwt")
        try:
            jwt = json.loads(verify_jwt(jwt, KEYSTORE, KEY_ID))
            ticket = db_manager.save_consent_request(jwt)
            return ticket
        except InvalidConsentRequestError as e:
            logger.debug("received invalid consent request: %s, %s", str(e), jwt)
            abort(400)

    @consent_api.route("/save_consent")
    def save_consent():
        state = request.args["state"]
        validation = "validation" in request.args
        consent_status = request.args["consent_status"]
        requester = session["requester_name"]
        user_id = session["user_id"]
        redirect_uri = session["redirect_endpoint"]
        month = request.args["month"]

        attributes = request.args.to_dict()
        if "validation" in attributes:
            attributes.pop("validation")
        attributes.pop("consent_status")
        attributes.pop("state")
        attributes.pop("month")

        for attr in session["locked_attrs"]:
            attributes[attr] = session["attr"][attr]

        if state != session["state"]:
            abort(403)
        if consent_status == "yes" and not set(attributes).issubset(
            set(session["attr"])
        ):
            abort(400)

        if consent_status == "yes" and validation:
            consent = Consent(attributes, user_id, requester, int(month))
            db_manager.save_consent(session["id"], consent)
            session.clear()

        if consent_status == "no":
            return redirect(cfg["redirect_url"])
        return redirect(redirect_uri)

    return consent_api
