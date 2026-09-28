from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import LitimeCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: LitimeCoordinator = entry.runtime_data
    async_add_entities([LitimeLoadSwitch(coordinator)])


class LitimeLoadSwitch(CoordinatorEntity[LitimeCoordinator], SwitchEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "dc_load"

    def __init__(self, coordinator: LitimeCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.address}_dc_load"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        return self.coordinator.load_on

    async def async_turn_on(self, **kwargs: object) -> None:
        await self.coordinator.async_set_load(True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: object) -> None:
        await self.coordinator.async_set_load(False)
        self.async_write_ha_state()
