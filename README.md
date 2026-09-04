# Rain Bird Integration for Unfolded Circle Remote 2/3

Control your **Rain Bird irrigation controllers** (equipped with an **LNK Wi-Fi module**) directly from your Unfolded Circle Remote 2 or Remote 3. Start and stop watering zones, set a rain delay, and monitor the rain sensor and the currently running zone - controlled **entirely locally** over your network with **no Rain Bird cloud account** required.

![Rain Bird](https://img.shields.io/badge/Rain%20Bird-Irrigation-2E7D32)
[![GitHub Release](https://img.shields.io/github/v/release/mase1981/uc-intg-rainbird?style=flat-square)](https://github.com/mase1981/uc-intg-rainbird/releases)
![License](https://img.shields.io/badge/license-MPL--2.0-blue?style=flat-square)
[![GitHub issues](https://img.shields.io/github/issues/mase1981/uc-intg-rainbird?style=flat-square)](https://github.com/mase1981/uc-intg-rainbird/issues)
[![Community Forum](https://img.shields.io/badge/community-forum-blue?style=flat-square)](https://unfolded.community/)
[![Discord](https://badgen.net/discord/online-members/zGVYf58)](https://discord.gg/zGVYf58)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/mase1981/uc-intg-rainbird/total?style=flat-square)
[![Buy Me A Coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=flat-square)](https://buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal-donate-blue.svg?style=flat-square)](https://paypal.me/mmiyara)
[![Github Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-30363D?&logo=GitHub-Sponsors&logoColor=EA4AAA&style=flat-square)](https://github.com/sponsors/mase1981)

## Supported Devices

Rain Bird irrigation controllers that use an **LNK** or **LNK2 Wi-Fi module** for local control, including the **ESP-TM2**, **ESP-Me / ESP-Me3**, **ESP-RZXe**, and other LNK-compatible controllers.

## Features

- **💧 Zone switches** - one switch per irrigation zone. Turn a zone on to start watering for your default duration; turn it off to stop all watering.
- **⏹️ Stop button** - stop watering on every zone at once.
- **🌧️ Rain delay selector** - set the rain delay from 0 to 14 days, and see the current setting.
- **📊 Sensors** - rain sensor (Wet/Dry), the currently running zone, remaining rain-delay days, and the controller model.
- **🔒 Fully local** - direct LAN control, no Rain Bird account and no cloud in the loop.
- **Multi-device** - add each Rain Bird controller on your network.

---
## ❤️ Support Development ❤️

If you find this integration useful, consider supporting development:

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub-pink?style=for-the-badge&logo=github)](https://github.com/sponsors/mase1981)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/mmiyara)

Your support helps maintain this integration. Thank you! ❤️
---

## How It Works

Rain Bird controllers with an LNK Wi-Fi module expose an encrypted local control API. This integration speaks that protocol directly:

- **No account, no cloud** - control runs entirely over your local network. Nothing is sent to Rain Bird's servers.
- **State follows the controller** - the running zone, rain sensor, and rain delay are polled from the device.
- **One request at a time** - the LNK module handles a single request at a time, so commands and status reads are serialised for reliability.

> Rain Bird controllers stop *all* watering with a single command, so turning off any zone switch (or pressing Stop Watering) stops every active zone.

## Requirements

- A Rain Bird controller with an LNK / LNK2 Wi-Fi module on the same network as your Remote.
- The **device password** you set in the Rain Bird app.
- Unfolded Circle Remote 2 / 3 with firmware supporting custom integrations.

## Installation

### Option 1: Remote Web Interface (Recommended)

1. Download the latest `uc-intg-rainbird-<version>.tar.gz` from the [**Releases**](https://github.com/mase1981/uc-intg-rainbird/releases) page.
2. Open your Remote's web interface (`http://your-remote-ip`).
3. Go to **Settings → Integrations → Add Integration → Install Custom** and upload the `.tar.gz`.

### Option 2: Docker (Advanced Users)

**Image**: `ghcr.io/mase1981/uc-intg-rainbird:latest`

**Docker Compose:**
```yaml
services:
  uc-intg-rainbird:
    image: ghcr.io/mase1981/uc-intg-rainbird:latest
    container_name: uc-intg-rainbird
    network_mode: host
    volumes:
      - ./config:/config
    environment:
      - UC_CONFIG_HOME=/config
      - UC_INTEGRATION_HTTP_PORT=9090
      - UC_INTEGRATION_INTERFACE=0.0.0.0
      - PYTHONPATH=/app
    restart: unless-stopped
```

**Docker Run:**
```bash
docker run -d --name uc-intg-rainbird --restart unless-stopped --network host -v $(pwd)/config:/config -e UC_CONFIG_HOME=/config -e UC_INTEGRATION_INTERFACE=0.0.0.0 -e UC_INTEGRATION_HTTP_PORT=9090 -e PYTHONPATH=/app ghcr.io/mase1981/uc-intg-rainbird:latest
```

## Configuration

1. Make sure your Rain Bird controller is **powered on** and on the same network as the Remote.
2. Start setup and enter the controller's **IP address**, its **device password**, and a **default watering time** in minutes.
3. Repeat setup to add additional controllers.

### Setup fields

**Host**
The IP address of your Rain Bird device. You can find the IP address under the device in the Rain Bird app under Controller Settings > Network Info.

**Password**
The controller password, which you set when the Rain Bird WiFi controller was first configured. This is not the password for your Rain Bird account. It is 4-8 letters or numbers; if you set it up with the Rain Bird 2.0 app, it is the 6-digit PIN.

**Default watering time**
How long a zone runs (in minutes) when you turn its switch on.

For each device the integration creates:

| Entity | Purpose |
|--------|---------|
| **Zone switches** (`<name> Zone N`) | Start a zone for the default duration; turn off to stop all watering. |
| **Stop button** (`<name> Stop Watering`) | Stop watering on every zone. |
| **Select** (`<name> Rain Delay`) | Set the rain delay (0–14 days) and view the current value. |
| **Sensors** | Rain sensor, active zone, rain-delay days, and controller model. |

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "Could not connect to a Rain Bird controller" | Check the IP address and device password, and make sure the controller is powered on and on the same network as the Remote. |
| Zone switch turns back off shortly after turning on | The controller reflects the previous state briefly after a command; the next poll shows the correct running zone. |
| Turning off one zone stops another zone | Rain Bird stops all watering with a single command; this is expected controller behavior. |
| Wrong number of zones | Zones are read from the controller on connect; re-run setup after changing your controller's station configuration. |

## Credits

- **Developer**: Meir Miyara
- **Rain Bird local protocol**: based on the [pyrainbird](https://github.com/allenporter/pyrainbird) library and the Home Assistant Rain Bird integration.
- **Unfolded Circle**: Remote 2/3 integration framework ([ucapi](https://github.com/unfoldedcircle/integration-python-library) / [ucapi-framework](https://github.com/JackJPowell/ucapi-framework)).

## License

Mozilla Public License 2.0 (MPL-2.0) - see the LICENSE file.

## Support & Community

- **GitHub Issues**: [Report bugs and request features](https://github.com/mase1981/uc-intg-rainbird/issues)
- **UC Community Forum**: [General discussion and support](https://unfolded.community/)
- **Developer**: [Meir Miyara](https://www.linkedin.com/in/meirmiyara)

---

**Made with ❤️ for the Unfolded Circle Community**

**Thank You**: Meir Miyara
