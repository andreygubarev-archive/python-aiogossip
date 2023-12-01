from aiogossip.codec import decode, encode


def test_encode_decode(message):
    encoded_message = encode(message)
    decoded_message = decode(encoded_message)
    assert decoded_message == message
