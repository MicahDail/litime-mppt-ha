from __future__ import annotations

from collections.abc import Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import LitimeCoordinator
from .parser import LitimeData


def _value(key: str) -> Callable[[LitimeCoordinator], float | int | None]:
    def getter(coordinator: LitimeCoordinator) -> float | int | None:
        data: LitimeData | None = coordinator.data
        if data is None:
            return None
        return getattr(data, key)

    return getter


SENSORS: tuple[tuple[SensorEntityDescription, Callable[[LitimeCoordinator], float | int | None]], ...] = (
    (
        SensorEntityDescription(
            key="battery_voltage",
            translation_key="battery_voltage",
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=1,
        ),
        _value("battery_voltage"),
    ),
    (
        SensorEntityDescription(
            key="battery_current",
            translation_key="battery_current",
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=2,
        ),
        _value("battery_current"),
    ),
    (
        SensorEntityDescription(
            key="battery_power",
            translation_key="battery_power",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=0,
        ),
        _value("battery_power"),
    ),
    (
        SensorEntityDescription(
            key="battery_soc",
            translation_key="battery_soc",
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.BATTERY,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=0,
        ),
        _value("battery_soc"),
    ),
    (
        SensorEntityDescription(
            key="controller_temperature",
            translation_key="controller_temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=0,
        ),
        _value("controller_temperature"),
    ),
    (
        SensorEntityDescription(
            key="load_voltage",
            translation_key="load_voltage",
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=1,
        ),
        _value("load_voltage"),
    ),
    (
        SensorEntityDescription(
            key="load_current",
            translation_key="load_current",
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=2,
        ),
        _value("load_current"),
    ),
    (
        SensorEntityDescription(
            key="load_power",
            translation_key="load_power",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=0,
        ),
        _value("load_power"),
    ),
    (
        SensorEntityDescription(
            key="pv_voltage",
            translation_key="pv_voltage",
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=1,
        ),
        _value("pv_voltage"),
    ),
    (
        SensorEntityDescription(
            key="max_charge_power",
            translation_key="max_charge_power",
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=0,
        ),
        _value("max_charge_power"),
    ),
    (
        SensorEntityDescription(
            key="energy_today",
            translation_key="energy_today",
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            suggested_display_precision=0,
        ),
        _value("energy_today"),
    ),
    (
        SensorEntityDescription(
            key="total_energy",
            translation_key="total_energy",
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            suggested_display_precision=0,
        ),
        _value("total_energy"),
    ),
    (
        SensorEntityDescription(
            key="running_days",
            translation_key="running_days",
            native_unit_of_measurement=UnitOfTime.DAYS,
            state_class=SensorStateClass.TOTAL_INCREASING,
            suggested_display_precision=0,
        ),
        _value("running_days"),
    ),
    (
        SensorEntityDescription(
            key="rssi",
            translation_key="rssi",
            native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            device_class=SensorDeviceClass.SIGNAL_STRENGTH,
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
        ),
        lambda coordinator: coordinator.rssi,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: LitimeCoordinator = entry.runtime_data
    async_add_entities(
        LitimeSensor(coordinator, description, getter)
        for description, getter in SENSORS
    )


class LitimeSensor(CoordinatorEntity[LitimeCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LitimeCoordinator,
        description: SensorEntityDescription,
        getter: Callable[[LitimeCoordinator], float | int | None],
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._getter = getter
        self._attr_unique_id = f"{coordinator.address}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> float | int | None:
        return self._getter(self.coordinator)
