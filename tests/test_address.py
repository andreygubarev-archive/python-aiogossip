import ipaddress

import pytest

from aiogossip.address import Address


def test_address_initialization():
    # Test initialization with correct types
    ip = ipaddress.ip_address("127.0.0.1")
    port = 8080
    address = Address(ip, port)
    assert address.ip == ip
    assert address.port == port

    # Test initialization with string IP
    assert Address("127.0.0.1", port).ip == ip

    # Test initialization with bytes IP
    assert Address(b"\x7f\x00\x00\x01", port).ip == ip

    # Test initialization with non-int port
    assert Address(ip, 8080.0).port == 8080
    assert Address(ip, "8080").port == 8080
    assert Address(ip, b"8080").port == 8080

    # Test initialization with incorrect types
    with pytest.raises(ValueError):
        Address("not an ip address", port)

    with pytest.raises(TypeError):
        Address([], port)

    with pytest.raises(TypeError):
        Address(ip, "port")
