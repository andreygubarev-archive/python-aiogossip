import dataclasses
import enum
import uuid
from typing import Any

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


def update_send_endpoints(message: Message, send: Endpoint, recv: Endpoint) -> Message:
    endpoints = message.route_endpoints

    if not endpoints:
        endpoints = [send, recv]
    elif endpoints[-1].node_id == send.route_id:
        endpoints.append(recv)

    endpoints[-2] = dataclasses.replace(endpoints[-2], saddr=send.saddr)
    endpoints[-1] = dataclasses.replace(endpoints[-1], daddr=recv.daddr)
    return dataclasses.replace(message, route_endpoints=endpoints)
