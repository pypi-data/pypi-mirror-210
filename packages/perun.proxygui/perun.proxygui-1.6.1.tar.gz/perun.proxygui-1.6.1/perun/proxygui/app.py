import jinja2
import yaml
from flask import Flask, request, session
from flask_babel import Babel

from perun.proxygui.api.ban_api import construct_ban_api_blueprint
from perun.proxygui.api.kerberos_auth_api import construct_kerberos_auth_api_blueprint
from perun.proxygui.gui.gui import construct_gui_blueprint


def get_config():
    try:
        with open(
            "/etc/perun.proxygui.yaml",
            "r",
            encoding="utf8",
        ) as ymlfile:
            cfg = yaml.safe_load(ymlfile)
    except IOError:
        with open(
            "config_templates/perun.proxygui.yaml",
            "r",
            encoding="utf8",
        ) as ymlfile:
            cfg = yaml.safe_load(ymlfile)

    return cfg


def get_flask_app(cfg):
    if "css_framework" not in cfg:
        cfg["css_framework"] = "bootstrap"

    if "bootstrap_color" not in cfg:
        cfg["bootstrap_color"] = "primary"

    def get_locale():
        if request.args.get("lang"):
            session["lang"] = request.args.get("lang")
        return session.get("lang", "en")

    app = Flask(__name__)
    app.jinja_loader = jinja2.FileSystemLoader("perun/proxygui/gui/templates")
    Babel(app, locale_selector=get_locale)

    app.secret_key = cfg["secret_key"]

    app.config["SERVER_NAME"] = cfg["host"]["server_name"]

    @app.context_processor
    def inject_conf_var():
        return dict(cfg=cfg, lang=get_locale())

    # Register GUI component
    app.register_blueprint(construct_gui_blueprint(cfg))

    # Register API endpoints
    app.register_blueprint(construct_ban_api_blueprint(cfg))
    app.register_blueprint(construct_kerberos_auth_api_blueprint(cfg))

    return app


# for uWSGI
def get_app(*args):
    cfg = get_config()
    app = get_flask_app(cfg)
    return app(*args)


if __name__ == "__main__":
    cfg = get_config()
    app = get_flask_app(cfg)
    app.run(
        host=cfg["host"]["ip-address"],
        port=cfg["host"]["port"],
        debug=cfg["host"]["debug"],
    )
