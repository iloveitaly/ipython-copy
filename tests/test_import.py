"""Test ipython-copy."""

import ipython_copy


def test_import() -> None:
    """Test that the  can be imported."""
    assert isinstance(ipython_copy.__name__, str)
