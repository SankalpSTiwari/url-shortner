import re

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
BASE = len(ALPHABET)
MIN_LENGTH = 7
ALIAS_RE = re.compile(r"^[a-zA-Z0-9_-]{3,16}$")


def base62_encode(num: int) -> str:
    if num == 0:
        return ALPHABET[0].ljust(MIN_LENGTH, ALPHABET[0])
    digits: list[str] = []
    while num:
        num, remainder = divmod(num, BASE)
        digits.append(ALPHABET[remainder])
    encoded = "".join(reversed(digits))
    return encoded.zfill(MIN_LENGTH)


def validate_custom_alias(alias: str) -> bool:
    return bool(ALIAS_RE.match(alias))
