# MODULE: aiogossip.transport

import pytest

from aiogossip.address import to_address
from aiogossip.transport import Transport


@pytest.mark.asyncio
async def test_transport_send_and_receive(event_loop):
    transport1 = Transport(to_address("127.0.0.1:0"), event_loop)
    transport2 = Transport(to_address("127.0.0.1:0"), event_loop)

    data = b"Hello, World!"
    await transport1.send(data, transport2.addr)

    received_data, received_addr = await transport2.recv()
    assert received_data == data
    assert received_addr == transport1.addr

    transport1.close()
    transport2.close()


@pytest.mark.asyncio
async def test_transport_send_large_data(event_loop):
    transport1 = Transport(to_address("127.0.0.1:0"), event_loop)
    transport2 = Transport(to_address("127.0.0.1:0"), event_loop)

    data = b"a" * (Transport.PACKET_SIZE + 1)
    with pytest.raises(ValueError):
        await transport1.send(data, transport2.addr)

    transport1.close()
    transport2.close()
