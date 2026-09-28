# LiTime MPPT for Home Assistant

Home Assistant custom integration for LiTime / HQST MPPT solar charge controllers that advertise as `BT-LTMPPT*` (for example `BT-LTMPPT4860`).

It uses Home Assistant’s Bluetooth stack, so an [ESPHome Bluetooth proxy](https://esphome.io/components/bluetooth_proxy/) with `active: true` works the same way [BMS_BLE-HA](https://github.com/patman15/BMS_BLE-HA) does for batteries. No ESPHome YAML changes are required.

Protocol mapping comes from [mavenius/litime_mppt_esphome](https://github.com/mavenius/litime_mppt_esphome).

## Requirements

- Home Assistant 2024.8 or later
- A connectable Bluetooth adapter or ESPHome Bluetooth proxy (`bluetooth_proxy: active: true`)
- The LiTime phone app disconnected (GATT is exclusive)
- One free BLE connection slot on the proxy (each BMS_BLE-HA pack already uses one)

## Install

### HACS (custom repository)

1. HACS → Integrations → ⋮ → Custom repositories
2. URL: https://github.com/MicahDail/litime-mppt-ha  
   Category: Integration
3. Download **LiTime MPPT**
4. Restart Home Assistant
5. Settings → Devices & services → Add integration → **LiTime MPPT**  
   Or accept the discovery notification for `BT-LTMPPT4860`

### Manual

Copy `custom_components/litime_mppt` into your Home Assistant `config/custom_components/` directory and restart.

## Entities

| Entity | Unit |
| --- | --- |
| Battery voltage / current / power | V / A / W |
| Battery SoC (16S LiFePO₄, 48.0–54.4 V) | % |
| Controller temperature | °C |
| Load voltage / current / power | V / A / W |
| PV input voltage | V |
| Max charging power today | W |
| Energy today / total | Wh |
| Running days | d |
| RSSI | dBm |
| DC load | switch |

## Troubleshooting

- Confirm the device in [Bluetooth Advertisement Monitor](https://my.home-assistant.io/redirect/bluetooth_advertisement_monitor)
- RSSI should be better than about −75 dBm
- Close the LiTime / vendor app
- Check proxy connection slots under Settings → Connectivity → Bluetooth
- Enable debug logs:

```yaml
logger:
  logs:
    custom_components.litime_mppt: debug
    bleak: debug
```

## License

GPL-3.0-or-later
