"""Test."""

from ha_addon_sma.helpers import pretty_print_dict


def test_pretty_print_dict() -> None:
    """Test pretty_print_dict."""
    data = {
        "serial": "123456",
        "protocol": "0x6069",
        "timestamp": 1622547800,
        "pconsume": 1000,
        "pconsumeunit": "W",
        "pconsumecounter": 5000,
        "pconsumecounterunit": "Wh",
        "psupply": 2000,
        "psupplyunit": "W",
    }
    assert pretty_print_dict(data) == {
        "serial": "123456",
        "protocol": "0x6069",
        "timestamp": "1622547800",
        "pconsume": "1000 W",
        "pconsumecounter": "5000 Wh",
        "psupply": "2000 W",
    }
