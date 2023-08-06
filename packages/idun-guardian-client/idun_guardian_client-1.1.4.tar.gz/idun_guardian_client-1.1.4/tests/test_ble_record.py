from unittest import mock
import pytest
import asyncio
import uuid

from idun_guardian_client import GuardianBLE

DEVICE = "BEE8A289-C6FF-81C5-B1E4-5709EB126125: IGEB"


async def find_device_by_address(address, timeout=10):
    return DEVICE


async def start_notify(data_handler):
    await data_handler()
    return 1


async def data_handler():
    while True:
        await asyncio.sleep(1)
        print("Callback")


guardian_ble = GuardianBLE()


@pytest.mark.asyncio
@mock.patch(
    "bleak.BleakScanner.find_device_by_address",  #
    return_value=find_device_by_address,
    new_callable=mock.PropertyMock,
)
# @mock.patch(
#     "bleak.BleakClient.start_notify",
#     return_value=start_notify(data_handler),
#     new_callable=mock.PropertyMock,
# )
@mock.patch("bleak.BleakClient.is_connected", return_value=True)
@mock.patch("bleak.BleakClient.connect", return_value=True)
@mock.patch("bleak.BleakClient.write_gatt_char", return_value=1)
@mock.patch("bleak.BleakClient.start_notify", return_value=1)
@mock.patch("bleak.BleakClient.disconnect", return_value=1)
async def test_run_ble_record(
    find_address_mock,
    start_notify_mock,
    is_connected_mock,
    connected_mock,
    write_gatt_char_mock,
    disconnect_mock,
):
    """
    GIVEN None
    WHEN run_ble_record is called
    THEN a list of BLE devices is returned
    """
    data_queue: asyncio.Queue = asyncio.Queue(maxsize=86400)
    recording_id = str(
        uuid.uuid4()
    )  # the recordingID is a unique ID for each recording

    mac_id = "F2-CC-34-BB-CC-00"
    ble_client_task = guardian_ble.run_ble_record(data_queue, 5, mac_id, True)

    # await asyncio.wait([ble_client_task])
