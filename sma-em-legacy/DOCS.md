# Configuration

## Parameters

- `SMA_SERIALS`

  This value can contain a space separated list of serial numbers for which to capture
  packets

  If you do not have the serial number for your Energy meter, you can run the add-on
  with an empty string. The add-on will now capture a debug packet and print the serial
  number found in that packet at the end of the log.

  Fill the number into `SMA_SERIALS` and run the addon again.

- `MQTT_*`

  You will need a working MQTT sevrer since all values will be sent via MQTT.
  The default configuration assumes the Mosquitto broker add-on and you simply have to
  fill in the password you configured there.

- `FIELDS`

  These can be any value supported by the SMA-EM library. A list of options can be found
  [below](*available-sensors)

- `DEBUG`

  The values received will continuously be printed to the add-on's log. This will confirm
  that you receive values for sensor `FIELDS` you configured.

  Recommended value: 0

## Available sensors

The following list contains all possible `FIELD` names that you can use with the add-on

| Name              | Unit  | Description                                  | Individual phases                                    |
|-------------------|-------|----------------------------------------------|------------------------------------------------------|
| pconsume          | W     | power consumed from the grid                 | p1consume, p2consume, p3consume                      |
| pconsumecounter   | kWh   | total energy consumed from the grid          | p1consumecounter, p2consumecounter, p3consumecounter |
| psupply           | W     | power supplied to the grid                   | p1supply, p2supply, p3supply                         |
| psupplycounter    | kWh   | total energy supplied to the grid            | p1supplycounter, p2supplycounter, p3supplycounter    |
| qconsume          | VAr   | reactive power consumed from the grid        | q1consume, q2consume, q3consume                      |
| qconsumecounter   | kVArh | total reactive energy consumed from the grid | q1consumecounter, q2consumecounter, q3consumecounter |
| qsupply           | VAr   | reactive power supplied to the grid          | q1supply, q2supply, q3supply                         |
| qsupplycounter    | kVArh | total reactive energy supplied to the grid   | q1supplycounter, q2supplycounter, q3supplycounter    |
| sconsume          | VA    | apparent power consumed from the grid        | s1consume, s2consume, s3consume                      |
| sconsumecounter   | kVAh  | total apparent energy consumed from the grid | s1consumecounter, s2consumecounter, s3consumecounter |
| ssupply           | VA    | apparent power supplied to the grid          | s1supply, s2supply, s3supply                         |
| ssupplycounter    | kVAh  | total apparent energy supplied to the grid   | s1supplycounter, s2supplycounter, s3supplycounter    |
| cosphi            |       | power factor                                 | cosphi1, cosphi2, cosphi3                            |
| frequency         | Hz    | grid frequency                               |                                                      |
|                   | A     | current                                      | i1, i2, i3                                           |
|                   | V     | voltage                                      | u1, u2, u3                                           |
| speedwire-version |       | version of the speedwire protocol            |                                                      |

> Note:
>
> Not all of these sensors units & types are correctly supported by auto-discovery
> today. You are welcome to add some & create a PR [here](https://github.com/kellerza/hassio-sma-em/blob/main/sma-em/run.py#L21)
>
> prefix: p=real power, q=reactive power, s=apparent power, i=current, u=voltage
> postfix: counter=energy value (kWh, kVArh, kVAh)
> without postfix counter=>power value (W, VAr, VA)

## Home Assistant Filters & utility meter

The values from the SMA sensor is updated every 5 seconds and this might fill up your
database fairly quickly.

Below is an example to reduce the frequency for these updates.

Assume `FIELDS=pconsume,pconsumecounter,u1`, and the auto-discovered sensors have been
renamed according to the table below

| Original name   | New name            | Description                     |
|-----------------|---------------------|---------------------------------|
| pconsume        | sma_grid_power_5s   | average power (W) last 1 minute |
| pconsumecounter | sma_grid_total_5s   | Total kWh value every 5 minutes |
| u1              | sma_grid_voltage_5s | average voltage last 30s        |

The utility meter will record these values and give you total energy used (kWh) every
day and every month.

Example filters & utility meter configuration.

```yaml
sensor:
  - platform: filter
    name: SMA Grid Power
    entity_id: sensor.sma_grid_power_5s
    filters:
      - filter: time_simple_moving_average
        window_size: 00:01

  - platform: filter
    name: SMA Grid Total
    entity_id: sensor.sma_grid_total_5s
    filters:
      - filter: time_throttle
        window_size: 00:05

  - platform: filter
    name: SMA Grid Voltage
    entity_id: sensor.sma_grid_voltage_5s
    filters:
      - filter: time_simple_moving_average
        window_size: 00:00:30

utility_meter:
  sma_daily_total:
    source: sensor.sma_grid_total
    cycle: daily
  sma_monthly_total:
    source: sensor.sma_grid_total
    cycle: monthly
```
