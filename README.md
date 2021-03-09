# Home Assistant SMA Energy Meter Add-On

An add-on to receive SMA Energy Meter measurements and push them to Home Assistant through MQTT. Support auto-discovery for the sensors. Uses the [SMA-EM](https://github.com/datenschuft/SMA-EM) library. 

Requires Home Assistant and a configured MQTT server

See the addon [README.md](sma-em/README.md) or [DOCS.md](sma-em/DOCS.md)

## Install

1. Add the following repository to your supervisor [![My: Add Repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fhassio-addons%2Frepository)

    ```
    https://github.com/kellerza/hassio-sma-em
    ```

2. Install the SMA Energy Meter & configure through the UI
