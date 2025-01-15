# Configuration (developer version)

## Parameters

- `SMA_DEVICES`

  This should contain of the list of devices and their prefix in Home Assistant

  Serial numbers not found in the configuration will be printed in the log

  Example:

  ```yaml
  SMA_DEVICES:
    - SERIAL_NR: 007
      PREFIX: sma
    - SERIAL_NR: 008
      PREFIX: sma2
  ```

- `FIELDS`

  These can be any value supported by the SMA-EM library. A list of options can be found
  [below](*available-sensors)

- `MQTT_*`

  You will need a working MQTT sevrer since all values will be sent via MQTT.
  The default configuration assumes the Mosquitto broker add-on and you simply have to
  fill in your password.

- `MCASTGRP`

  Multicast address that is configured in the SMA Energy Meter. Default value is 239.12.255.254.

- `IPBIND`

  Multicast address that is configured in the SMA Energy Meter. Default value is 239.12.255.254.

- `THRESHOLD`

  Used for smart sensors, see the field modifiers below.

- `RECONNECT_INTERVAL`

  Interval to reconnect to the SMA Energy Meter. Default value is 86400 seconds.

- `DEBUG`

  The values received will continuously be printed to the add-on's log. This will confirm
  that you receive values for sensor `FIELDS` you configured.

  Recommended value: 0

## Available sensors

The following list contains all possible values you can include in `FIELDS`

```text
pconsume,  pconsumecounter,
psupply,   psupplycounter,
qconsume,  qconsumecounter,
qsupply,   qsupplycounter,
sconsume,  sconsumecounter,
ssupply,   ssupplycounter,
cosphi,
frequency,
p1consume, p1consumecounter,
p1supply,  p1supplycounter,
q1consume, q1consumecounter,
q1supply,  q1supplycounter,
s1consume, s1consumecounter,
s1supply,  s1supplycounter,
i1,
u1,
cosphi1,
p2consume, p2consumecounter,
p2supply,  p2supplycounter,
q2consume, q2consumecounter,
q2supply,  q2supplycounter,
s2consume, s2consumecounter,
s2supply,  s2supplycounter,
i2,
u2,
cosphi2,
p3consume, p3consumecounter,
p3supply,  p3supplycounter,
q3consume, q3consumecounter,
q3supply,  q3supplycounter,
s3consume, s3consumecounter,
s3supply,  s3supplycounter,
i3,
u3,
cosphi3,
speedwire-version
```

> Note:
>
> Not all of these sensors units & types are correctly supported by auto-discovery
> today. You are welcome to add some & create a PR [here](https://github.com/kellerza/hassio-sma-em/blob/main/sma-em/sensors.py#L21)
>
> prefix: p=real power, q=reactive power, s=apparent power, i=current, u=voltage
> postfix: unit=the unit of the item, e.g. W, VA, VAr, Hz, A, V, kWh, kVArh, kVAh ...
> postfix: counter=energy value (kWh, kVArh, kVAh)
> without postfix counter=>power value (W, VAr, VA)

## Sensor modifiers - Min/Max/Average/Smart

Sensors fields can be modified by adding a modifier to the end of the field name.
Without any modifier, the sensor will have a smart interval.
The average will be reported every 60 seconds.
If there are a big change (more than `THRESHOLD` or less than 2\*`THRESHOLD`) the value
will be reported immediately.
These type of fields can be used in automations that will respond within the measurement
interval of the SMA Energy meter (1 second)

Other modifiers

| Modifier | Description                                                                                                                        |
| -------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| `:max`   | the maximum value over the last 60 seconds. <br/> Ideal for **counters** where you are typically interested only in the last value |
| `:min`   | the minimum value over the last 60 seconds.                                                                                        |
| `:<s>`   | any integer will allow you to get the average over the indicated amount of seconds. `:5`=5 seconds, `:60`=60 seconds               |

## Home Assistant Utility meter

The utility meter can be used to calaculate kwH usage per-day and per-month on
consume**counter** fields

Add a **FIELDS** entry: `pconsumecounter:max` will give you the max counter value over
the last 60 seconds

The utility meter will record these values and give you total energy used (kWh) every
day and every month.

Example utility meter configuration.

```yaml
utility_meter:
  sma_daily_total:
    source: sensor.pconsumecounter
    cycle: daily
  sma_monthly_total:
    source: sensor.pconsumecounter
    cycle: monthly
```
