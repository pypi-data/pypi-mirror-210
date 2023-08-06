from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC as _PBKDF2HMAC
from cryptography.hazmat.backends import default_backend as _default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM as _AESGCM
from cryptography.hazmat.primitives.hashes import SHA256 as _SHA256
from secrets import token_bytes as _token_bytes
from typing import Any

from ..utils import evaluate as _evaluate


# add base64 fixed
# add compression (lz4?)


def keygen(material: Any = None) -> bytes:
    if not material:
        return _token_bytes(32)
    kdf = _PBKDF2HMAC(_SHA256(), 32, b'', 100000, _default_backend())
    return kdf.derive(str(material).encode())


def encrypt(
        raw: Any,
        key: bytes = keygen(),
        masterkey: Any = None,
        authdata: Any = None
) -> tuple[bytes, bytes]:
    nonce = _token_bytes(12)
    authdata = str(authdata).encode() if authdata else b''
    encrypted = nonce + _AESGCM(key).encrypt(nonce, str(raw).encode(), authdata)
    if masterkey:
        key, _ = encrypt(raw=key, key=keygen(masterkey))
    return encrypted, key


def decrypt(
        encrypted: bytes,
        key: bytes,
        masterkey: Any = None,
        authdata: Any = None,
        *,
        evaluate: bool = False
) -> Any:
    if masterkey:
        key = decrypt(encrypted=key, key=keygen(masterkey), evaluate=True)
    authdata = str(authdata).encode() if authdata else b''
    decrypted = _AESGCM(key).decrypt(encrypted[:12], encrypted[12:], authdata)
    return _evaluate(decrypted, evaluate)
