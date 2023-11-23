import pytest

from aiogossip.router import Router


@pytest.mark.asyncio
async def test_subscribe(gossips):
    gossip = gossips[0]
    router = Router(gossip)
    await router.subscribe()
