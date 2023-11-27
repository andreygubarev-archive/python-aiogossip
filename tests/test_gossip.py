import asyncio

import pytest

# from aiogossip.gossip import Gossip
# from aiogossip.transport import Transport


@pytest.mark.asyncio
async def test_gossip(gossips):
    message = {"message": "", "metadata": {}}
    await gossips[0].gossip(message)

    async def listener(gossip):
        try:
            async with asyncio.timeout(0.1):
                async for message in gossip.recv():
                    pass
        except asyncio.TimeoutError:
            pass

    listeners = [asyncio.create_task(listener(n)) for n in gossips]
    await asyncio.gather(*listeners)

    for gossip in gossips:
        if gossip.topology.node == gossips[0].topology.node:
            continue
        if any([gossip.topology.node in p.topology for p in gossips]):
            assert gossip.transport.rx_packets > 0, gossip.topology
    rx_packets = sum(p.transport.rx_packets for p in gossips)
    assert rx_packets <= 2 ** len(gossips)

    for gossip in gossips:
        gossip.transport.close()


# @pytest.mark.asyncio
# async def test_send_and_receive(event_loop):
#     def get_transport():
#         return Transport(("localhost", 0), loop=event_loop)

#     gossips = [Gossip(get_transport(), []) for _ in range(2)]
#     message = {"message": "Hello, world!", "metadata": {}}

#     await gossips[0].send(message, gossips[1].topology.node)
#     received_message = await anext(gossips[1].recv())
#     assert received_message["message"] == message["message"]
