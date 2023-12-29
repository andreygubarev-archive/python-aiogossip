import dataclasses
import uuid

from .endpoint import Endpoint


@dataclasses.dataclass
class PeerEndpoint:
    id: uuid.UUID
    endpoint: Endpoint

    def __post_init__(self):
        if not isinstance(self.id, uuid.UUID):
            raise TypeError("id must be an instance of uuid.UUID")

        if not self.id.version == 1:
            raise ValueError("id must be a version 1 UUID")

        if not isinstance(self.endpoint, Endpoint):
            raise TypeError("endpoint must be an instance of Endpoint")
