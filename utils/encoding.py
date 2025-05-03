import base64


def str_encode(text: str) -> str:
    encoded = base64.b64encode(text.encode()).decode()
    return encoded


def str_decode(text: str) -> str:
    decoded = base64.b64decode(text.encode()).decode()
    return decoded
