import dataclasses
import ipaddress

import pytest

from aiogossip.address import Address


def test_post_init():
    # Test with valid IPv4 address and port
    address = Address(ipaddress.IPv4Address("192.168.1.1"), 8080)
    assert isinstance(address.ip, ipaddress.IPv4Address)
    assert isinstance(address.port, int)

    # Test with valid IPv6 address and port
    address = Address(ipaddress.IPv6Address("2001:0db8:85a3:0000:0000:8a2e:0370:7334"), 8080)
    assert isinstance(address.ip, ipaddress.IPv6Address)
    assert isinstance(address.port, int)

    # Test with invalid IP
    with pytest.raises(TypeError):
        Address("invalid_ip", 8080)

    # Test with invalid port
    with pytest.raises(TypeError):
        Address(ipaddress.IPv4Address("192.168.1.1"), "invalid_port")

    # Test frozen
    with pytest.raises(dataclasses.FrozenInstanceError):
        address.ip = ipaddress.IPv4Address("127.0.0.1")

    # Test slots
    with pytest.raises(AttributeError):
        address.invalid_attribute

    with pytest.raises(TypeError):
        address.invalid_attribute = "test"

    # Test frozen replacement
    address = dataclasses.replace(address, ip=ipaddress.IPv4Address("192.168.0.1"))
    assert address.ip == ipaddress.IPv4Address("192.168.0.1")


def test_parse_ip():
    # Test with valid IPv4 address
    ip = Address.parse_ip("192.168.1.1")
    assert isinstance(ip, ipaddress.IPv4Address)

    # Test with valid IPv6 address
    ip = Address.parse_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334")
    assert isinstance(ip, ipaddress.IPv6Address)

    # Test with valid IPv4Address object
    ip = Address.parse_ip(ipaddress.IPv4Address("192.168.1.1"))
    assert isinstance(ip, ipaddress.IPv4Address)

    # Test with valid IPv6Address object
    ip = Address.parse_ip(ipaddress.IPv6Address("2001:0db8:85a3:0000:0000:8a2e:0370:7334"))
    assert isinstance(ip, ipaddress.IPv6Address)

    # Test with invalid IP type
    with pytest.raises(TypeError):
        Address.parse_ip(123)

    # Test with invalid IP format
    with pytest.raises(ValueError):
        Address.parse_ip("invalid_ip")

    # Test with invalid IP address
    with pytest.raises(ValueError):
        Address.parse_ip("256.0.0.1")

    # Test with invalid IP address
    with pytest.raises(ValueError):
        Address.parse_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334:1234")


def test_parse_port():
    # Test with valid integer port
    port = Address.parse_port(8080)
    assert isinstance(port, int)
    assert 0 <= port <= 65535

    # Test with valid string port
    port = Address.parse_port("8080")
    assert isinstance(port, int)
    assert 0 <= port <= 65535

    # Test with valid bytes port
    port = Address.parse_port(b"8080")
    assert isinstance(port, int)
    assert 0 <= port <= 65535

    # Test with valid float port
    port = Address.parse_port(8080.0)
    assert isinstance(port, int)
    assert 0 <= port <= 65535

    # Test with invalid port
    with pytest.raises(ValueError):
        Address.parse_port("invalid_port")

    # Test with port out of range
    with pytest.raises(ValueError):
        Address.parse_port(70000)

    # Test with negative port
    with pytest.raises(ValueError):
        Address.parse_port(-1)

    # Test with non-numeric string
    with pytest.raises(ValueError):
        Address.parse_port("not_a_number")

    # Test with non-numeric bytes
    with pytest.raises(ValueError):
        Address.parse_port(b"not_a_number")

    # Test with invalid type
    with pytest.raises(TypeError):
        Address.parse_port([])
