# Changelog

## **2024.5.10** - 2024-05-10
- Added Multicast Adress as an Option Field


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

### Changed

- Removed state_class and last_reset and added AUTODISCOVER_OPTIONS, where auto-discovery
  attributes like state_class and last reset can be added once supported.

## **2021.8.0** - 2021-08-04

### Changed

- Add state_class and last_reset to support energy measurements
  [long term stats](https://developers.home-assistant.io/blog/2021/05/25/sensor_attributes/)
