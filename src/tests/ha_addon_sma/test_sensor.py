"""Test sensor."""

from ha_addon_sma.sensors import SWSensor


def test_sensor() -> None:
    """Test sensor modifiers."""
    s = SWSensor("Test Sensor", mod="1")
    assert s.name == "Test Sensor"
    assert s.id == "test_sensor_1"
    assert s.mod == "avg"
    assert s.interval == 1

    s = SWSensor("Test Sensor", mod="max")
    assert s.name == "Test Sensor"
    assert s.id == "test_sensor_max"
    assert s.mod == "max"
    assert s.interval == 60
