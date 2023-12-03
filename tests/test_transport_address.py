import ipaddress

import pytest

from aiogossip.transport.address import Address, parse_addr


def test_parse_addr_with_address_object():
    addr = Address(ipaddress.ip_address("127.0.0.1"), 8000)
    assert parse_addr(addr) == addr


def test_parse_addr_with_tuple():
    addr = ("127.0.0.1", 8000)
    expected = Address(ipaddress.ip_address("127.0.0.1"), 8000)
    assert parse_addr(addr) == expected


def test_parse_addr_with_string():
    addr = "127.0.0.1:8000"
    expected = Address(ipaddress.ip_address("127.0.0.1"), 8000)
    assert parse_addr(addr) == expected


def test_parse_addr_with_invalid_type():
    with pytest.raises(TypeError):
        parse_addr(123)
