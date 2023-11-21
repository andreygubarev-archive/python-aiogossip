import pytest

from aiogossip.transport import Transport


@pytest.mark.asyncio
async def test_send_recv():
    transport = Transport(("localhost", 0))

    message = {"key": "value"}
    addr = transport.sock.getsockname()
    await transport.send(message, addr)

    received_message, received_addr = await transport.recv()
    assert received_message == message
    assert received_addr == addr
