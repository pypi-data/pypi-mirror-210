import json

import jwt
import requests
from jwt.algorithms import ECAlgorithm, RSAAlgorithm

from django_jwt import settings


def _get_public_keys() -> dict:
    certs_data = requests.get(settings.JWT_CERTS_URL).json()
    public_keys = {}
    for key_data in certs_data["keys"]:
        if key_data["kty"] == "RSA":
            public_keys[key_data["alg"]] = RSAAlgorithm.from_jwk(json.dumps(key_data))
        elif key_data["kty"] == "EC":
            public_keys[key_data["alg"]] = ECAlgorithm.from_jwk(json.dumps(key_data))
    return public_keys


class KCVerifier:
    _public_key = None

    @property
    def public_key(self) -> str:
        if self._public_key is None:
            keys = _get_public_keys()
            self._public_key = keys[settings.JWT_ALGORITHM]
        return self._public_key

    def verify_token(self, token: str) -> dict:
        return jwt.decode(
            token,
            key=self.public_key,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            options={"verify_aud": False},
        )


verifier = KCVerifier()
