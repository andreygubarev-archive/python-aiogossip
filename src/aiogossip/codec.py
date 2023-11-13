import json


def decode(data):
    return json.loads(data.decode())


def encode(data):
    return json.dumps(data).encode()
