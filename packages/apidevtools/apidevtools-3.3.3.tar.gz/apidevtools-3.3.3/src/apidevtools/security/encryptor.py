from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC as _PBKDF2HMAC
from cryptography.hazmat.backends import default_backend as _default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM as _AESGCM
from cryptography.hazmat.primitives.hashes import SHA256 as _SHA256
from secrets import token_bytes as _token_bytes
from typing import Any

from ..utils import evaluate as _evaluate


# add base64 ?
# review types of `material`, `masterkey`, `authdata`, `raw`

def keygen(material: Any = None) -> bytes:
    if not material:
        return _token_bytes(32)
    kdf = _PBKDF2HMAC(_SHA256(), 32, b'', 1, _default_backend())
    return kdf.derive(str(material).encode())


def encrypt(
        raw: Any,
        key: bytes = keygen(),
        masterkey: Any = None,
        authdata: Any = None,
        *,
        compressed: bool = False
) -> tuple[bytes, bytes]:
    nonce: bytes = _token_bytes(12)
    raw: bytes = str(raw).encode()
    if compressed:  # compressing before to encrypt faster
        import lz4.block as compressor
        raw = compressor.compress(raw)
    encrypted: bytes = nonce + _AESGCM(key).encrypt(nonce, raw, str(authdata).encode() if authdata else b'')
    if masterkey:  # encrypting encryption key using master key
        key, _ = encrypt(raw=key, key=keygen(masterkey))
    return encrypted, key


def decrypt(
        encrypted: bytes,
        key: bytes,
        masterkey: Any = None,
        authdata: Any = None,
        *,
        compressed: bool = False,
        evaluate: bool = False
) -> Any:
    if masterkey:
        key: bytes = eval(decrypt(encrypted=key, key=keygen(masterkey)))
    decrypted: bytes = _AESGCM(key).decrypt(encrypted[:12], encrypted[12:], str(authdata).encode() if authdata else b'')
    if compressed:
        import lz4.block as compressor
        decrypted = compressor.decompress(decrypted)
    return _evaluate(decrypted, evaluate)
