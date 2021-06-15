# Home Assistant SMA Energy Meter Add-On

An add-on to receive SMA Energy Meter measurements and push them to Home Assistant through MQTT. Support auto-discovery for the sensors.
Uses the Speedwire decoder from the [SMA-EM](https://github.com/datenschuft/SMA-EM) project.

Requires Home Assistant and a configured MQTT server

See the addon [README.md](sma-em/README.md) or [DOCS.md](sma-em/DOCS.md)

## Install

1. Add the repository to your supervisor

   ```text
   https://github.com/kellerza/hassio-sma-em
   ```

   Quickly install via: [![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fkellerza%2Fhassio-sma-em)

2. Install the SMA Energy Meter & configure through the UI

## Updating to a newer version

Home Assistant OS will check for new versions periodically.

You can force this by navigating to the **Add-on Store** and in the top-right hand
corner click on the three vertical dots **&vellip;**. This will open a menu with a **Reload** option.
