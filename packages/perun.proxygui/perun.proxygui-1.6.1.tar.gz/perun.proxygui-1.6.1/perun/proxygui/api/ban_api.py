import io
import json
from http import HTTPStatus
from typing import Any
import gzip

import flask
import sqlalchemy
import tarfile
from bson.json_util import dumps
from flask import Blueprint, request, Response
from perun.connector import AdaptersManager
from perun.connector import Logger
from pymongo import MongoClient
from pymongo.collection import Collection
from sqlalchemy import delete
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session

from perun.utils.ConfigStore import ConfigStore

logger = Logger.get_logger(__name__)


def get_mongo_db_collection(cfg, cfg_db_name: str) -> Collection:
    client = MongoClient(cfg[cfg_db_name]["connection_string"])
    database_name = cfg[cfg_db_name]["database_name"]
    collection_name = cfg[cfg_db_name]["collection_name"]

    return client[database_name][collection_name]


def get_ban_collection(cfg) -> Collection:
    return get_mongo_db_collection(cfg, "ban_database")


def get_satosa_sessions_collection(cfg) -> Collection:
    return get_mongo_db_collection(cfg, "satosa_database")


def get_ssp_sessions_collection(cfg) -> Collection:
    return get_mongo_db_collection(cfg, "ssp_database")


def revoke_ssp_sessions(subject: str, ssp_sessions_collection: Collection) -> int:
    result = ssp_sessions_collection.delete_many({"user": subject})
    return result.deleted_count


def revoke_satosa_grants(subject: str, satosa_sessions_collection: Collection) -> int:
    result = satosa_sessions_collection.delete_many({"sub": subject})

    return result.deleted_count


def get_postgres_engine(cfg) -> Engine:
    connection_string = cfg["mitre_database"]["connection_string"]
    engine = sqlalchemy.create_engine(connection_string)

    return engine


def get_mitre_delete_statements(user_id: str, engine: Engine) -> list[Any]:
    meta_data = sqlalchemy.MetaData(bind=engine)
    sqlalchemy.MetaData.reflect(meta_data)

    AUTH_HOLDER_TBL = meta_data.tables["authentication_holder"]
    SAVED_USER_AUTH_TBL = meta_data.tables["saved_user_auth"]

    ACCESS_TOKEN_TBL = meta_data.tables["access_token"]
    delete_access_tokens_stmt = delete(ACCESS_TOKEN_TBL).where(
        ACCESS_TOKEN_TBL.auth_holder_id.in_(
            Session.query(AUTH_HOLDER_TBL.id).filter(
                AUTH_HOLDER_TBL.user_auth_id.in_(
                    Session.query(SAVED_USER_AUTH_TBL.id).filter(
                        SAVED_USER_AUTH_TBL.name == user_id
                    )
                )
            )
        )
    )

    AUTH_CODE_TBL = meta_data.tables["authorization_code"]
    delete_authorization_codes_stmt = delete(AUTH_CODE_TBL).where(
        AUTH_CODE_TBL.auth_holder_id.in_(
            Session.query(AUTH_HOLDER_TBL.id).filter(
                AUTH_HOLDER_TBL.user_auth_id.in_(
                    Session.query(SAVED_USER_AUTH_TBL.id).filter(
                        SAVED_USER_AUTH_TBL.name == user_id
                    )
                )
            )
        )
    )

    DEVICE_CODE = meta_data.tables["device_code"]
    delete_device_codes_stmt = delete(DEVICE_CODE).where(
        DEVICE_CODE.auth_holder_id.in_(
            Session.query(AUTH_HOLDER_TBL.id).filter(
                AUTH_HOLDER_TBL.user_auth_id.in_(
                    Session.query(SAVED_USER_AUTH_TBL.id).filter(
                        SAVED_USER_AUTH_TBL.name == user_id
                    )
                )
            )
        )
    )

    return [
        delete_access_tokens_stmt,
        delete_authorization_codes_stmt,
        delete_device_codes_stmt,
    ]


def delete_mitre_tokens(cfg, user_id: str) -> int:
    deleted_mitre_tokens_count = 0

    engine = get_postgres_engine(cfg)
    statements = get_mitre_delete_statements(user_id, engine)

    for stmt in statements:
        result = engine.execute(stmt)
        deleted_mitre_tokens_count += result.rowcount

    return deleted_mitre_tokens_count


def logout_user(
    user_id: str,
    ssp_sessions_collection: Collection,
    satosa_sessions_collection: Collection,
    adapters_manager: AdaptersManager,
    subject_attribute: str,
    cfg,
):
    user_attrs = adapters_manager.get_user_attributes(int(user_id), [subject_attribute])
    subject_candidates = user_attrs.get(subject_attribute, [])
    subject = subject_candidates[0] if subject_candidates else None

    revoked_sessions_count = revoke_ssp_sessions(subject, ssp_sessions_collection)
    revoked_grants_count = revoke_satosa_grants(subject, satosa_sessions_collection)
    deleted_tokens_count = delete_mitre_tokens(cfg, user_id)

    logger.info(
        f"Logged out user {subject} from {revoked_sessions_count} SSP "
        f"sessions, deleted {revoked_grants_count} SATOSA sessions and "
        f"deleted {deleted_tokens_count} mitre tokens."
    )


def is_ban_in_db(ban_id: int, ban_collection: Collection) -> bool:
    return ban_collection.find_one({"id": ban_id}) is not None


def remove_outdated_bans_from_db(banned_users, ban_collection: Collection):
    current_ban_ids = [ban["id"] for ban in banned_users.values()]
    ban_collection.delete_many({"id": {"$nin": current_ban_ids}})


def construct_ban_api_blueprint(cfg):
    ban_api = Blueprint("ban_api", __name__)

    GLOBAL_CONFIG = ConfigStore.get_global_cfg(cfg.get("global_cfg_filepath"))
    ADAPTERS_MANAGER_CFG = GLOBAL_CONFIG["adapters_manager"]
    ATTRS_MAP = ConfigStore.get_attributes_map(GLOBAL_CONFIG["attrs_cfg_path"])
    ADAPTERS_MANAGER = AdaptersManager(ADAPTERS_MANAGER_CFG, ATTRS_MAP)
    PERSON_PRINCIPAL_NAMES_ATTRIBUTE = cfg.get("perun_person_principal_names_attribute")
    UPLOAD_FILE_MAX_SIZE = int(cfg.get("max_ban_upload_filesize"))

    # Endpoints
    @ban_api.route("/banned-users/", methods=["PUT"])
    def update_banned_users() -> Response:
        process_update(request.get_json())

        response = flask.Response()
        response.headers["Cache-Control"] = "public, max-age=0"
        response.status_code = HTTPStatus.NO_CONTENT

        return response

    @ban_api.route("/banned-users-generic/", methods=["PUT"])
    def update_banned_users_generic() -> Response:
        if request.content_length > UPLOAD_FILE_MAX_SIZE:
            logger.warn(
                f"Request too large: {str((request.content_length // 1024) // 1024)} MB"
            )
            response = flask.make_response(
                "Request too large!", HTTPStatus.REQUEST_ENTITY_TOO_LARGE
            )
            response.headers["Cache-Control"] = "public, max-age=0"
            return response

        banned_users = None
        banned_users_tar_filepath = "./banned_facility_users"
        io_bytes = io.BytesIO(request.get_data())
        gzip_file = gzip.GzipFile(fileobj=io_bytes)
        try:
            with tarfile.open(fileobj=gzip_file) as tar:
                for tarinfo in tar:
                    if tarinfo.isreg() and tarinfo.name == banned_users_tar_filepath:
                        ban_file = tarinfo.path
                        with tar.extractfile(ban_file) as f:
                            content = f.read()
                            banned_users = json.loads(content)
        except Exception as ex:
            logger.warn("Could not parse banned users data: ", ex)
            return flask.make_response(
                f"Could not parse banned users data: {ex}",
                HTTPStatus.UNPROCESSABLE_ENTITY,
            )

        if banned_users is None:
            logger.warn("Banned users file not found in the request.")
            response = flask.make_response(
                "Banned users file not found in the request.",
                HTTPStatus.UNPROCESSABLE_ENTITY,
            )
            response.headers["Cache-Control"] = "public, max-age=0"
            return response

        process_update(banned_users)

        logger.info("Banned users successfully updated.")
        response = flask.Response()
        response.headers["Cache-Control"] = "public, max-age=0"
        response.status_code = HTTPStatus.NO_CONTENT
        return response

    def process_update(banned_users) -> None:
        ban_collection = get_ban_collection(cfg)
        ssp_sessions_collection = get_ssp_sessions_collection(cfg)
        satosa_sessions_collection = get_satosa_sessions_collection(cfg)

        remove_outdated_bans_from_db(banned_users, ban_collection)

        for user_id, ban in banned_users.items():
            if not is_ban_in_db(int(ban["id"]), ban_collection):
                logout_user(
                    user_id,
                    ssp_sessions_collection,
                    satosa_sessions_collection,
                    ADAPTERS_MANAGER,
                    PERSON_PRINCIPAL_NAMES_ATTRIBUTE,
                    cfg,
                )
            ban_collection.replace_one({"id": ban["id"]}, ban, upsert=True)
        logger.debug(f"User bans updated: {dumps(ban_collection.find())}")

    @ban_api.route("/ban/<ban_id>", methods=["GET"])
    def find_ban(ban_id: str) -> str:
        ban_collection = get_ban_collection(cfg)
        found_ban = ban_collection.find_one({"id": int(ban_id)})

        return dumps(found_ban) if found_ban else dumps({})

    return ban_api
