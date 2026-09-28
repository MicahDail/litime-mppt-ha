from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING

from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.exc import BleakError
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_ble_device_from_address,
    async_last_service_info,
)
from homeassistant.components.bluetooth.const import DOMAIN as BLUETOOTH_DOMAIN
from homeassistant.const import CONF_ADDRESS
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CHAR_UUID,
    DOMAIN,
    LOGGER,
    NOTIFY_TIMEOUT,
    POLL_CMD,
    UPDATE_INTERVAL,
)
from .parser import LitimeData, expected_frame_length, parse_response

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


class LitimeCoordinator(DataUpdateCoordinator[LitimeData]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            LOGGER,
            name=entry.title,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
            config_entry=entry,
        )
        self.address: str = entry.data[CONF_ADDRESS]
        self._client: BleakClientWithServiceCache | None = None
        self._event = asyncio.Event()
        self._buf = bytearray()
        self._latest: LitimeData | None = None
        self._load_on = True
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, self.address), (BLUETOOTH_DOMAIN, self.address)},
            connections={(CONNECTION_BLUETOOTH, self.address)},
            name=entry.title,
            manufacturer="LiTime",
            model=entry.title,
        )

    @property
    def rssi(self) -> int | None:
        service_info: BluetoothServiceInfoBleak | None = async_last_service_info(
            self.hass, address=self.address, connectable=True
        )
        return service_info.rssi if service_info else None

    @property
    def load_on(self) -> bool:
        return self._load_on

    async def async_shutdown(self) -> None:
        await super().async_shutdown()
        await self._async_disconnect()

    async def async_set_load(self, enabled: bool) -> None:
        from .const import LOAD_OFF_CMD, LOAD_ON_CMD

        await self._async_ensure_connected()
        assert self._client is not None
        cmd = LOAD_ON_CMD if enabled else LOAD_OFF_CMD
        await self._client.write_gatt_char(CHAR_UUID, cmd, response=False)
        self._load_on = enabled

    async def _async_disconnect(self) -> None:
        client = self._client
        self._client = None
        if client is None:
            return
        try:
            await client.disconnect()
        except BleakError:
            LOGGER.debug("Disconnect failed for %s", self.address, exc_info=True)

    async def _async_ensure_connected(self) -> None:
        if self._client is not None and self._client.is_connected:
            return
        ble_device = async_ble_device_from_address(self.hass, self.address, True)
        if ble_device is None:
            raise UpdateFailed(f"Bluetooth device {self.address} not found")
        self._client = await establish_connection(
            BleakClientWithServiceCache,
            ble_device,
            self.name,
            max_attempts=3,
        )
        await self._client.start_notify(CHAR_UUID, self._notification)

    def _notification(
        self, _char: BleakGATTCharacteristic, data: bytearray
    ) -> None:
        if data.startswith(b"\x01\x03"):
            self._buf = bytearray(data)
        else:
            self._buf.extend(data)
        expected = expected_frame_length(self._buf)
        payload = bytes(self._buf)
        parsed = None
        if expected is not None and len(self._buf) >= expected:
            parsed = parse_response(payload[:expected])
            self._buf.clear()
        elif len(self._buf) >= 42:
            parsed = parse_response(payload)
            if parsed is not None:
                self._buf.clear()
        if parsed is None:
            return
        self._latest = parsed
        self._event.set()

    async def _async_update_data(self) -> LitimeData:
        self._buf.clear()
        self._event.clear()
        try:
            await self._async_ensure_connected()
            assert self._client is not None
            await self._client.write_gatt_char(CHAR_UUID, POLL_CMD, response=False)
            async with asyncio.timeout(NOTIFY_TIMEOUT):
                await self._event.wait()
        except TimeoutError as err:
            await self._async_disconnect()
            raise UpdateFailed("Timed out waiting for MPPT data") from err
        except BleakError as err:
            await self._async_disconnect()
            raise UpdateFailed(f"Bluetooth error: {err}") from err
        if self._latest is None:
            raise UpdateFailed("No MPPT data received")
        return self._latest
