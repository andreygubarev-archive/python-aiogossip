import ipaddress

import pytest

from aiogossip.transport import Address


@pytest.mark.asyncio
async def test_send_recv(transport, message):
    await transport.send(message, transport.addr)

    received_message, received_addr = await transport.recv()
    assert received_message == message
    assert received_addr == transport.addr

    transport.close()


@pytest.mark.asyncio
async def test_send_large_packet(transport, message):
    message.id = b"a" * (transport.PACKET_SIZE + 1)

    with pytest.raises(ValueError) as excinfo:
        await transport.send(message, transport.addr)

    expected = f"Message size exceeds packet size of {transport.PACKET_SIZE} bytes: 4100"
    assert str(excinfo.value) == expected


@pytest.mark.asyncio
async def test_send_type_errors(transport, message):
    with pytest.raises(TypeError):
        await transport.send(message, ("127.0.0.1", 1337))

    with pytest.raises(TypeError):
        await transport.send(message, Address("127.0.0.1", 1337))

    with pytest.raises(TypeError):
        await transport.send(message, Address(ipaddress.ip_address("127.0.0.1"), 1337.0))


@pytest.mark.asyncio
async def test_parse_addr_with_address(transport):
    addr = Address("127.0.0.1", 1337)
    result = transport.parse_addr(addr)
    assert result == addr


@pytest.mark.asyncio
async def test_parse_addr_with_tuple(transport):
    addr = ("127.0.0.1", 1337)
    result = transport.parse_addr(addr)
    assert result == Address(ipaddress.ip_address(addr[0]), int(addr[1]))


@pytest.mark.asyncio
async def test_parse_addr_with_string(transport):
    addr = "127.0.0.1:1337"
    result = transport.parse_addr(addr)
    ip, port = addr.split(":")
    assert result == Address(ipaddress.ip_address(ip), int(port))


@pytest.mark.asyncio
async def test_parse_addr_with_invalid_type(transport):
    addr = None
    with pytest.raises(TypeError) as excinfo:
        transport.parse_addr(addr)
    assert str(excinfo.value) == f"Address must be a Address, tuple or str, got: {type(addr)}"
