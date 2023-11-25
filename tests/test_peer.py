import pytest


@pytest.mark.parametrize("randomize", [0])
@pytest.mark.parametrize("instances", [1])
def test_peer(peers):
    peer = peers[0]
    assert peer.identity is not None
