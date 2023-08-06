from .funcs.sha256 import sha256
from .funcs.b32 import base32e
from .funcs.b64 import base64e
from .funcs.vigenere import cypher
from .funcs.salter import get_salt


def encode(mess: str, method: str = "sha", key: str = "crypt", salty: bool = False) -> str:
    """
    Encodes or hashes a message.
    Takes in the message, the method, key and whether you want the hash or encoding to be salted all as strings except for the salt, it has to be True.
    Methods available: SHA256 (sha or sha256), BASE32 (b32 or base32), BASE64 (b64 or base64), VIGENERE (vig or vigenere).
    Defaults the method to SHA256, the key to crypt, the salt to False.
    """
    if salty == True:
        salt = get_salt()
    else:
        salt = ""
    mess += salt
    if method == "sha" or method == "sha256":
        return f"sha256${salt}${sha256(mess)}"
    elif method == "base32" or method == "b32":
        return f"base32${salt}${base32e(mess)}"
    elif method == "base64" or method == "b64":
        return f"base64${salt}${base64e(mess)}"
    elif method == "vigenere" or method == "vig":
        return f"vig${salt}${cypher(mess, key)}"
    else:
        return "I can't currently encode with that method"