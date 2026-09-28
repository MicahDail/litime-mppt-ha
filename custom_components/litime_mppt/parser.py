from __future__ import annotations

from dataclasses import dataclass

from .const import SOC_MAX_VOLTAGE, SOC_MIN_VOLTAGE


@dataclass(frozen=True, slots=True)
class LitimeData:
    battery_voltage: float
    battery_current: float
    battery_power: float
    controller_temperature: float
    load_voltage: float
    load_current: float
    load_power: float
    pv_voltage: float
    max_charge_power: float
    energy_today: float
    running_days: int
    total_energy: float
    battery_soc: float


def _u16(data: bytes, offset: int) -> int:
    return (data[offset] << 8) | data[offset + 1]


def expected_frame_length(data: bytes | bytearray) -> int | None:
    if len(data) < 3 or data[0] != 0x01 or data[1] != 0x03:
        return None
    return 5 + data[2]


def parse_response(data: bytes) -> LitimeData | None:
    if len(data) < 42 or data[0] != 0x01 or data[1] != 0x03:
        return None
    voltage = _u16(data, 5) * 0.1
    span = SOC_MAX_VOLTAGE - SOC_MIN_VOLTAGE
    soc = max(0.0, min(100.0, (voltage - SOC_MIN_VOLTAGE) / span * 100.0))
    return LitimeData(
        battery_voltage=round(voltage, 1),
        battery_current=round(_u16(data, 7) * 0.01, 2),
        battery_power=float(_u16(data, 9)),
        controller_temperature=float(data[11]),
        load_voltage=round(_u16(data, 13) * 0.1, 1),
        load_current=round(_u16(data, 15) * 0.01, 2),
        load_power=float(_u16(data, 17)),
        pv_voltage=round(_u16(data, 19) * 0.1, 1),
        max_charge_power=float(_u16(data, 21)),
        energy_today=float(_u16(data, 23)),
        running_days=_u16(data, 31),
        total_energy=float(_u16(data, 35)),
        battery_soc=round(soc),
    )
