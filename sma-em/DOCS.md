# Configuration

## Parameters

- `SMA_SERIALS`

  This value can contain a space seperated list of serial numbers for which to capture
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

  The values received will continously be printed to the add-on's log. This will confirm
  that you receive values for sensor `FIELDS` you configured.

  Recommended value: 0

## Available sensors

The following list contains all possible `FIELD` names that you can use with the add-on

```text
pconsume,  pconsumeunit, pconsumecounter, pconsumecounterunit,
psupply,   psupplyunit,  psupplycounter,  psupplycounterunit,
qconsume,  qconsumeunit, qconsumecounter, qconsumecounterunit,
qsupply,   qsupplyunit,  qsupplycounter,  qsupplycounterunit,
sconsume,  sconsumeunit, sconsumecounter, sconsumecounterunit,
ssupply,   ssupplyunit,  ssupplycounter,  ssupplycounterunit,
cosphi,    cosphiunit,
frequency, frequencyunit,
p1consume, p1consumeunit, p1consumecounter, p1consumecounterunit,
p1supply,  p1supplyunit,  p1supplycounter,  p1supplycounterunit,
q1consume, q1consumeunit, q1consumecounter, q1consumecounterunit,
q1supply,  q1supplyunit,  q1supplycounter,  q1supplycounterunit,
s1consume, s1consumeunit, s1consumecounter, s1consumecounterunit,
s1supply,  s1supplyunit,  s1supplycounter,  s1supplycounterunit,
i1,        i1unit,
u1,        u1unit,
cosphi1,   cosphi1unit,
p2consume, p2consumeunit, p2consumecounter, p2consumecounterunit,
p2supply,  p2supplyunit,  p2supplycounter,  p2supplycounterunit,
q2consume, q2consumeunit, q2consumecounter, q2consumecounterunit,
q2supply,  q2supplyunit,  q2supplycounter,  q2supplycounterunit,
s2consume, s2consumeunit, s2consumecounter, s2consumecounterunit,
s2supply,  s2supplyunit,  s2supplycounter,  s2supplycounterunit,
i2,        i2unit,
u2,        u2unit,
cosphi2,   cosphi2unit,
p3consume, p3consumeunit, p3consumecounter, p3consumecounterunit,
p3supply,  p3supplyunit,  p3supplycounter,  p3supplycounterunit,
q3consume, q3consumeunit, q3consumecounter, q3consumecounterunit,
q3supply,  q3supplyunit,  q3supplycounter,  q3supplycounterunit,
s3consume, s3consumeunit, s3consumecounter, s3consumecounterunit,
s3supply,  s3supplyunit,  s3supplycounter,  s3supplycounterunit,
i3,        i3unit,
u3,        u3unit,
cosphi3,   cosphi3unit,
speedwire-version
```

> Note:
>
> Not all of these sensors units & types are correctly supported by auto-discovery
> today. You are welcome to add some & create a PR [here](https://github.com/kellerza/hassio-sma-em/blob/main/sma-em/run.py#L21)
>
> prefix:  p=real power, q=reactive power, s=apparent power, i=current, u=voltage
> postfix: unit=the unit of the item, e.g. W, VA, VAr, Hz, A, V, kWh, kVArh, kVAh ...
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
