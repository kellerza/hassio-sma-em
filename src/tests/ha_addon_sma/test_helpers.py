"""Test."""

from ha_addon_sma.helpers import inject_pgrid, pretty_print_dict


def test_inject_pgrid() -> None:
    """Test signed grid power derivation."""
    data = {"pconsume": 1000, "pconsumeunit": "W", "psupply": 2000, "psupplyunit": "W"}
    inject_pgrid(data)
    assert data["pgrid"] == -1000
    assert data["pgridunit"] == "W"

    data = {"pconsume": 3000, "psupply": 500}
    inject_pgrid(data)
    assert data["pgrid"] == 2500
    assert data["pgridunit"] == "W"

    missing = {"pconsume": 1000}
    inject_pgrid(missing)
    assert "pgrid" not in missing

    missing = {"psupply": 1000}
    inject_pgrid(missing)
    assert "pgrid" not in missing


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
