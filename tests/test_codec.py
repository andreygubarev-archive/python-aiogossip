import uuid

from aiogossip.codec import decode, encode
from aiogossip.message_pb2 import Message


def test_encode_decode():
    message = Message()
    message.metadata.id = uuid.uuid4().bytes

    encoded_message = encode(message)
    decoded_message = decode(encoded_message)
    assert decoded_message == message
