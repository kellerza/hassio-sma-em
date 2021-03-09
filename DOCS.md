## Configuration

The default config will contain no SMA_SERIALS, but this has to be populated.

On first run a debug packet will be captured and the serial number will be printed in the add-on's LOG tab.


## HomeAssistant Filters & utility meter

Example filters & utility meter configuration.

```yaml
sensor:
  - platform: filter
    name: grid power 1min
    entity_id: sensor.grid_power
    filters:
      - filter: time_simple_moving_average
        window_size: 00:01

  - platform: filter
    name: total yield 5min
    entity_id: sensor.total_yield
    filters:
      - filter: time_throttle
        window_size: 00:05

utility_meter:
  daily_yield:
    source: sensor.total_yield
    cycle: daily
  monthly_yield:
    source: sensor.total_yield
    cycle: monthly
```