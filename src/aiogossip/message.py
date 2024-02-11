class Message:
    """A message is a packet of data sent from one broker to another."""

    def __init__(self, data: bytes):
        self.data = data

    def __eq__(self, other):
        return self.data == other.data

    def __repr__(self):
        return f"<Message data={self.data}>"

    def __str__(self):
        return self.data.decode("utf-8")


def to_message(data: bytes) -> Message:
    return Message(data)
