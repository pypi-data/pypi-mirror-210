from .funcs.b32 import base32d
from .funcs.b64 import base64d
from .funcs.vigenere import decypher


def decode(mess: str, method='b32', key: str = 'crypt'):
    """
    Decodes a message.
    Takes in the message, the method, and the key if needed for the method.
    Methods available: BASE32 (b32 or base32), BASE64 (b64 or base64), VIGENERE (vig or vigenere).
    Defaults the method to BASE32, the key to crypt.
    """
    if method == 'base32' or method == 'b32':
        return base32d(mess)
    elif method == 'base64' or method == 'b64':
        return base64d(mess)
    elif method == 'vigenere' or method == 'vig':
        return (decypher(mess, key))
    else:
        return "I can't currently decode with that method"
    
