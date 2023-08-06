import json

from flask import Blueprint
from flask import render_template, make_response, jsonify
from flask_babel import gettext

from perun.proxygui.jwt import verify_jwt


def construct_gui_blueprint(cfg):
    gui = Blueprint("gui", __name__, template_folder="templates")

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

    return gui
