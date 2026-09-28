from __future__ import annotations

import logging

DOMAIN = "litime_mppt"
LOGGER = logging.getLogger(__package__)

LOCAL_NAME_PREFIX = "BT-LTMPPT"
UPDATE_INTERVAL = 10
NOTIFY_TIMEOUT = 10
SOC_MIN_VOLTAGE = 48.0
SOC_MAX_VOLTAGE = 54.4

SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"

POLL_CMD = bytes((0x01, 0x03, 0x01, 0x01, 0x00, 0x13, 0x54, 0x3B))
LOAD_ON_CMD = bytes((0x01, 0x06, 0x01, 0x20, 0x00, 0x01, 0x48, 0x3C))
LOAD_OFF_CMD = bytes((0x01, 0x06, 0x01, 0x20, 0x00, 0x00, 0x89, 0xFC))


def is_supported_name(name: str | None) -> bool:
    return bool(name) and name.upper().startswith(LOCAL_NAME_PREFIX)
