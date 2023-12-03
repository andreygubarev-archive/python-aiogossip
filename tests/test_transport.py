import pytest


@pytest.mark.asyncio
async def test_send_recv(transport, message):
    addr = transport.sock.getsockname()
    await transport.send(message, addr)

    received_message, received_addr = await transport.recv()
    assert received_message == message
    assert received_addr == addr


@pytest.mark.asyncio
async def test_send_large_payload(transport, message):
    message.id = b"a" * (transport.PAYLOAD_SIZE + 1)
    addr = transport.sock.getsockname()

    with pytest.raises(ValueError) as excinfo:
        await transport.send(message, addr)

    expected = f"Message size exceeds payload size of {transport.PAYLOAD_SIZE} bytes"
    assert str(excinfo.value) == expected


@pytest.mark.asyncio
async def test_addr_property(transport):
    assert transport.addr == transport.sock.getsockname()
    assert transport.addr[0] == "127.0.0.1"
    assert isinstance(transport.addr[1], int)
