import dataclasses
import enum
import uuid
from typing import Any

import typeguard

from .endpoint import Endpoint


class Kind(enum.Enum):
    HANDSHAKE = 0
    GOSSIP = 1


@dataclasses.dataclass(frozen=True, slots=True)
class Message:
    route_snode: uuid.UUID
    route_dnode: uuid.UUID
    route_endpoints: list[Endpoint] = dataclasses.field(default_factory=list)

    message_id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    message_type: set[Kind] = dataclasses.field(default_factory=set)

    payload: Any | None = None


@typeguard.typechecked
def update_send_endpoints(message: Message, send: Endpoint, recv: Endpoint) -> Message:
    """
    Update source address of sender and destination address of receiver in a message.

    Args:
        message (Message): The message to update.
        send (Endpoint): The endpoint of the sender.
        recv (Endpoint): The endpoint of the receiver.

    Returns:
        Message: The updated message with the new send and receive endpoints.
    """
    endpoints = message.route_endpoints

    if not endpoints:
        endpoints = [send, recv]
    elif endpoints[-1].node == send.node:
        endpoints.append(recv)

    endpoints[-2] = dataclasses.replace(endpoints[-2], saddr=send.saddr)
    endpoints[-1] = dataclasses.replace(endpoints[-1], daddr=recv.daddr)
    return dataclasses.replace(message, route_endpoints=endpoints)


@typeguard.typechecked
def update_recv_endpoints(message: Message, send: Endpoint, recv: Endpoint) -> Message:
    """
    Update destination address of sender and source address of receiver in a message.

    Args:
        message (Message): The message to update.
        send (Endpoint): The endpoint of the sender.
        recv (Endpoint): The endpoint of the receiver.

    Returns:
        Message: The updated message with the new send and receive endpoints.
    """
    endpoints = message.route_endpoints
    endpoints[-2] = dataclasses.replace(endpoints[-2], daddr=send.daddr)
    endpoints[-1] = dataclasses.replace(endpoints[-1], saddr=recv.saddr)
    return dataclasses.replace(message, route_endpoints=endpoints)
