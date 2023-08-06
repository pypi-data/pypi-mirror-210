from jwcrypto import jwk, jwt
from jwcrypto.jwk import JWKSet, JWK


def import_keys(file_path: str) -> JWKSet:
    jwk_set = jwk.JWKSet()
    with open(file_path, "r") as file:
        jwk_set.import_keyset(file.read())
    return jwk_set


def get_signing_jwk(file: str, key: str) -> JWK:
    jwk_set = import_keys(file)
    return jwk_set.get_key(key)


def verify_jwt(token, keystore, key_id):
    jwk_key = get_signing_jwk(keystore, key_id)
    return jwt.JWT(jwt=token, key=jwk_key).claims
