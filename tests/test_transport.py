import pytest


@pytest.mark.asyncio
async def test_send_recv(transport, message):
    await transport.send(message, transport.addr)

    received_message, received_addr = await transport.recv()
    assert received_message == message
    assert received_addr == transport.addr


@pytest.mark.asyncio
async def test_send_large_packet(transport, message):
    message.id = b"a" * (transport.PACKET_SIZE + 1)

    with pytest.raises(ValueError) as excinfo:
        await transport.send(message, transport.addr)

    expected = f"Message size exceeds packet size of {transport.PACKET_SIZE} bytes: 4100"
    assert str(excinfo.value) == expected
