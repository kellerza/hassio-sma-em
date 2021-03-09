## Configuration

The default config will contain no SMA_SERIALS, but this has to be populated.

On first run a debug packet will be captured and the serial number will be printed in the add-on's LOG tab.

## Available sensors

```
The following list contains all possible field names that you can use with
the features mqtt, symcon, influxdb
  prefix:  p=real power, q=reactive power, s=apparent power, i=current, u=voltage
  postfix: unit=the unit of the item, e.g. W, VA, VAr, Hz, A, V, kWh, kVArh, kVAh ...
  postfix: counter=energy value (kWh, kVArh, kVAh)
           without postfix counter=>power value (W, VAr, VA)
mqttfields=pconsume,  pconsumeunit, pconsumecounter, pconsumecounterunit,
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