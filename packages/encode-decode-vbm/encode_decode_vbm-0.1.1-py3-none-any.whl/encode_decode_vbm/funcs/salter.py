from random import SystemRandom


def get_salt(length: int = 16) -> str:
    SALT_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    salt = "".join(SystemRandom().choice(SALT_CHARS) for _ in range(length))

    return salt
