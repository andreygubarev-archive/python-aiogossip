from aiogossip.codec import decode, encode


def test_decode():
    data = b'{"key": "value"}'
    expected = {"key": "value"}
    assert decode(data) == expected


def test_encode():
    data = {"key": "value"}
    expected = b'{"key": "value"}'
    assert encode(data) == expected


def test_encode_decode():
    data = {"key": "value"}
    encoded = encode(data)
    decoded = decode(encoded)
    assert decoded == data
