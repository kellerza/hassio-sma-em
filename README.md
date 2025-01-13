# Home Assistant SMA Energy Meter Add-On

An add-on to receive SMA Energy Meter measurements and push them to Home Assistant through MQTT. Support auto-discovery for the sensors.
Uses the Speedwire decoder from the [SMA-EM](https://github.com/datenschuft/SMA-EM) project.

Requires Home Assistant OS and a configured MQTT server

Inside the Supervisor tab in HomeAssistant you can get more information in each add-on's [README.md](sma-em/README.md) or [DOCS.md](sma-em/DOCS.md) files

## Installation

1. Add the repository to your Supervisor
   <br>[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fkellerza%2Fhassio-sma-em)
   `https://github.com/kellerza/hassio-sma-em` <br><br>

2. Install the SMA Energy Meter from the **Add-On Store** & configure through the UI

## Frequently Asked Questions

### Updating to a new version

Home Assistant OS will check for new versions periodically.

You can force this by navigating to the **Add-on Store** and in the top-right hand
corner click on the three vertical dots **&vellip;**. This will open a menu with a **Reload** option.

### Debugging

#### 1. Add-on

You can set debug mode in the configuration options - `DEBUG: 1`. If you change this configuration you have to restart the add-on

The log should now include all values that will be sent to MQTT

#### 2. MQTT

You can use a MQTT Explorer on Windows to connect to your MQTT server and view the persistent messages (added during auto-discovery) and the received values

#### 3. HomeAssistant

You need to enable MQTT and auto-discovery. Please refer to the HomeAssistant docs

## Addons

There are three versions of the addon

* SMA Energy Meter
    The recommended stable release
* SMA Energy Meter (developer version)
    The latest changes
* SMA Energy Meter (Legacy)
    Won't receive any future updates. Uses SMA-EM directly. You can try this is you are unable to receive multicast frame with the other versions.

## Contributing

Contributions are welcome, please limit these to the developer version in the `sma-em-dev` folder.

Pre-commit should be used to ensure formatting is consistent when a change is committed.

```bash
pre-commit install
```
