from .message_pb2 import Message


def decode(data):
    return Message.FromString(data)


def encode(data):
    return data.SerializeToString()
