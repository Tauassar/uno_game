import base64
import hashlib
import hmac
import json
import secrets
import typing

import bcrypt
import cryptography.fernet
import fastapi.security
import itsdangerous

from ..core import conf
from ..core import times
from . import schemas


oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl='/api/v1/token')


_BCRYPT_SALT_ROUNDS = 12
_BCRYPT_SALT_PREFIX = b'2b'


class InvalidToken(Exception):
    """Raises if invalid token was provided."""


class InvalidData(Exception):
    """Raises if invalid data was provided."""


def compute_password_hash(password: str) -> str:
    """Compute hash for provided password."""
    return bcrypt.hashpw(
        hashlib.sha256(password.encode()).hexdigest().encode(),
        bcrypt.gensalt(
            rounds=_BCRYPT_SALT_ROUNDS,
            prefix=_BCRYPT_SALT_PREFIX,
        ),
    ).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify hash correctness for provided password."""
    return bcrypt.checkpw(
        hashlib.sha256(plain_password.encode()).hexdigest().encode(),
        hashed_password.encode(),
    )


def gen_random_token(nbytes: int = 32) -> str:
    """Generate URL-safe string with n bytes of randomness."""
    return secrets.token_urlsafe(nbytes)


def get_signer(secret_key: str, salt: str):
    """Return preconfigured signer with sane defaults."""
    return itsdangerous.URLSafeTimedSerializer(
        secret_key,
        salt=salt,
        signer_kwargs={
            'key_derivation': 'hmac',
            'digest_method': hashlib.sha256,
        },
    )


def sign_token(
    token_data: dict,
    secret_key: str,
    salt: str = 'token',
) -> str:
    """Sign provided token data."""
    signer = get_signer(secret_key, salt)

    return signer.dumps(token_data)


def unsign_token(
    token: str,
    secret_key: str,
    expires_in: int,
    salt: str = 'token',
) -> dict:
    """Unsign provided token."""
    signer = get_signer(secret_key, salt)
    try:
        return signer.loads(token, max_age=expires_in)
    except itsdangerous.BadSignature:
        raise InvalidToken


def extract_client_id_from_signed_token(
    token: str,
    secret_key: str = conf.security.secret_key,
    expires_in: int = conf.security.token_expires_in_seconds,
) -> typing.Optional[int]:
    """Extract client id from token, preliminarily validating the token signature."""
    try:
        return unsign_token(token, secret_key, expires_in).get('cid')
    except InvalidToken:
        return None


def issue_access_token(
    client_id: int,
    secret_key: str = conf.security.secret_key,
    expires_in: int = conf.security.token_expires_in_seconds,
) -> schemas.AccessTokenInternal:
    """Issue access token."""
    issued_at = times.utcnow()
    signed_token = sign_token(
        token_data={'cid': client_id},
        secret_key=secret_key,
    )

    return schemas.AccessTokenInternal(
        client_id=client_id,
        token=signed_token,
        is_revoked=False,
        token_type='bearer',
        issued_at=issued_at,
        expires_in=expires_in,
    )


def issue_refresh_token(client_id: int) -> schemas.RefreshTokenInternal:
    """Issue refresh token."""

    return schemas.RefreshTokenInternal(
        client_id=client_id,
        token=gen_random_token(),
        is_revoked=False,
        token_type='bearer',
        issued_at=times.utcnow(),
    )


def serialize_payload(payload: dict, signature_ttl: int) -> bytes:
    payload['ts'] = int(times.utcnow().timestamp())
    payload['ttl'] = signature_ttl

    return json.dumps(payload, sort_keys=True).encode('ascii')


def sign_payload(
    payload: bytes, secret_key: str, digest: str = 'sha256',
) -> typing.Tuple[str, str]:
    """Returns hmac signed payload and payload signature"""
    private_key: bytes = secret_key.encode('ascii')
    signed_payload: str = itsdangerous.base64_encode(payload).decode('ascii')
    signature: str = itsdangerous.base64_encode(
        hmac.digest(
            key=private_key,
            msg=payload,
            digest=digest,
        ),
    ).decode('ascii')

    return signed_payload, signature


def encrypt(payload: dict, secret_key: str) -> bytes:
    secret_key_hashed = base64.urlsafe_b64encode(
        hashlib.sha256(secret_key.encode()).digest(),
    )
    return cryptography.fernet.Fernet(secret_key_hashed).encrypt(
        itsdangerous.Serializer(secret_key_hashed).dumps(
            payload,
        ).encode('utf-8'),
    )


def decrypt(data: bytes, secret_key: str, ttl: typing.Optional[int] = None) -> typing.Dict:
    try:
        secret_key_hashed = base64.urlsafe_b64encode(
            hashlib.sha256(secret_key.encode()).digest(),
        )
        data = cryptography.fernet.Fernet(secret_key_hashed).decrypt(data, ttl)
        return itsdangerous.Serializer(secret_key_hashed).loads(data)
    except (cryptography.fernet.InvalidToken, itsdangerous.BadData):
        raise InvalidData
