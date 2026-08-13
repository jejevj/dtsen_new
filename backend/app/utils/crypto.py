import base64


DTSEN_SECRET_KEY = "DTSEN#Secure2026"


def encrypt_identifier(value: str) -> str | None:
    if value is None:
        return None

    value = str(value)

    result = bytearray()

    key = DTSEN_SECRET_KEY.encode("utf-8")
    data = value.encode("utf-8")

    for i, b in enumerate(data):

        k = key[i % len(key)]

        x = b ^ k
        x = (x + ((i * 17) % 256)) % 256
        x ^= 0x5A

        result.append(x)

    return base64.urlsafe_b64encode(result).decode("utf-8")


def decrypt_identifier(value: str) -> str | None:

    if value is None:
        return None

    data = base64.urlsafe_b64decode(value)

    key = DTSEN_SECRET_KEY.encode("utf-8")

    result = bytearray()

    for i, b in enumerate(data):

        x = b ^ 0x5A

        x = (x - ((i * 17) % 256)) % 256

        k = key[i % len(key)]

        x ^= k

        result.append(x)

    return result.decode("utf-8")