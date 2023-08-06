from unittest import mock
from collections import namedtuple
import pytest
import yaml
from idun_guardian_client import GuardianBLE
import os

with open(
    "tests/mocked_bluetooth/mocked_bluetooth.yaml", "r", encoding="utf-8"
) as file:
    config = yaml.safe_load(file)


def dictToObject(d):
    """
    This function converts a dictionary to an object
    """
    for k, v in d.items():
        if isinstance(v, dict):
            d[k] = dictToObject(v)
    return namedtuple("object", d.keys())(*d.values())


client = dictToObject(config)


def mock_discover_function():
    """
    This function returns a list of functions
    """
    return ["Device 1", "Device 2"]


@pytest.mark.asyncio
@mock.patch(
    "bleak.BleakScanner.discover",
    return_value=mock_discover_function,
    side_effect=mock.AsyncMock,
)
async def test_get_ble_devices(mock_discover):
    """
    GIVEN None
    WHEN get_ble_devices is called
    THEN a list of BLE devices is returned
    """
    assert isinstance(await GuardianBLE().get_ble_devices(), list)


@pytest.mark.asyncio
@mock.patch(
    "bleak.BleakClient.services",
    return_value=client.services,
    new_callable=mock.PropertyMock,
)
@mock.patch("bleak.BleakClient.read_gatt_char", return_value=1)
@mock.patch("bleak.BleakClient.connect", return_value=True)
async def test_device_information(mock_services, mock_read_gatt_char, mock_connect):
    """
    GIVEN None
    WHEN device_information is called
    THEN None
    """
    ble = GuardianBLE()
    print(ble)

    device_info = [
        "Model Number String",
        "Serial Number String",
        "Firmware Revision String",
        "Hardware Revision String",
        "Software Revision String",
        "Manufacturer Name String",
    ]
    device_info_ble = await ble.get_device_information()
    assert len(device_info_ble) == len(device_info)
    for info in device_info:
        assert type(device_info_ble[info]) == str
