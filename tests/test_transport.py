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


@pytest.mark.asyncio
async def test_send_large_payload():
    transport = Transport(("localhost", 0))

    message = "a" * (transport.PAYLOAD_SIZE + 1)
    addr = transport.sock.getsockname()

    with pytest.raises(ValueError) as excinfo:
        await transport.send(message, addr)

    expected = f"Message size exceeds payload size of {transport.PAYLOAD_SIZE} bytes"
    assert str(excinfo.value) == expected
