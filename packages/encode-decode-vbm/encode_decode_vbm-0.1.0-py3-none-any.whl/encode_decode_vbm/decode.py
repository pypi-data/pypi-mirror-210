from .funcs.b32 import base32d
from .funcs.b64 import base64d
from .funcs.vigenere import decypher


def decode(mess: str, method='sha', key: str = 'crypt'):
    if method == 'sha':
        return 'I can\'t decode SHA!'
    elif method == 'base32' or method == 'b32':
        return base32d(mess)
    elif method == 'base64' or method == 'b64':
        return base64d(mess)
    elif method == 'vigenere' or method == 'vig':
        return (decypher(mess, key))
    else:
        return 'I can\'t currently decode with that method'
