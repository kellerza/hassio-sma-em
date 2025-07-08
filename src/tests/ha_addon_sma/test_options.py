"""Tests."""

from ha_addon_sma.options import OPT


def test_import() -> None:
    """Test import."""
    assert OPT is not None, "OPT should be imported successfully"
