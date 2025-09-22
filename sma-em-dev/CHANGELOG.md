# Changelog

<https://github.com/kellerza/hassio-sma-em/releases>

## **2025.7.x**

- Update MQTT discovery to device based discovery (requires a MQTT LWT option with retain!)
- Update container to s6 overlay
- Build all containers

## **2025.1.14** - 2025-01-15

- Improve HA discovery. Add state_class to support statistics.
- Use `SMA_DEVICES` instead of `SMA_SERIALS`. This allows you to control the HA prefix if you have multiple SMA devices
- Minor changes to the speedwiredecoder library

## **2025.1.13** - 2025-01-13

- Added Address to bind to as an option (useful if you have multiple addresses). The default is `0.0.0.0`
- If `SMA_SERIALS` is not empty, serial numbers not in this list will be ignored

## **2024.5.10** - 2024-05-10

- Added Multicast Address as an Option Field

## **2023.5.18** - 2023-05-18

- Removed round - Issue #27

## **2023.4.16** - 2023-04-16

- sma-em-dev version
  - Updated MQTT library to mqtt_entity. Enables removal of discovery sensors
  - Ignore speedwire packets with no measurements
  - Updated pre-commit & typing info

## **dev**

- Removed AUTODISCOVER_OPTIONS

## **2021.8.1** - 2021-08-05

- Removed state_class and last_reset and added AUTODISCOVER_OPTIONS, where auto-discovery
  attributes like state_class and last reset can be added once supported.

## **2021.8.0** - 2021-08-04

- Add state_class and last_reset to support energy measurements
  [long term stats](https://developers.home-assistant.io/blog/2021/05/25/sensor_attributes/)
