"""
Misc utility functions
"""

import platform


def check_platform():
    """
    Check if the script is running on a cross platform

    Returns:
        bool: True if running on cross platform
    """
    if platform.system() == "Darwin":
        return "Darwin"
    elif platform.system() == "Linux":
        return "Linux"
    elif platform.system() == "Windows":
        return "Windows"
    else:
        raise Exception("Unsupported platform")


def check_valid_mac(mac_address: str) -> bool:
    """Check if mac address is valid

    Args:
        mac_address (str): Mac address

    Returns:
        bool: True if mac address is valid
    """
    if len(mac_address) != 17:
        return False
    if mac_address.count(":") != 5:
        return False
    print("Mac address is valid")
    return True


def check_valid_uuid(uuid: str) -> bool:
    """Check if uuid is valid

    Args:
        uuid (str): UUID
    """
    if len(uuid) != 36:
        return False
    if uuid.count("-") != 4:
        return False
    return True


def unpack_from_queue(package):
    """Unpack data from the queue filled with BLE data

    Args:
        package (dict): BLE data package

    Returns:
        timestamp: Timestamp of the data
        deviceID: Device ID of the data
        data: Data from the BLE package
        stop: Boolean to stop the cloud streaming
        impedance: Impedance data
    """
    # check if "timestamp" is in the package
    if "timestamp" in package:
        timestamp = package["timestamp"]
    else:
        timestamp = None

    # chek if deviceID is in the package
    if "deviceID" in package:
        device_id = package["deviceID"]
    else:
        device_id = None

    # check if "data" is in the package
    if "data" in package:
        data = package["data"]
    else:
        data = None

    # check if "type" is in the package
    if "stop" in package:
        stop = package["stop"]
    else:
        stop = None

    # check if impedance is in the package
    if "impedance" in package:
        impedance = package["impedance"]
    else:
        impedance = None

    return (timestamp, device_id, data, stop, impedance)


async def unpack_and_load_data(data_model, data_queue):
    """Get data from the queue and pack it into a dataclass"""
    package = await data_queue.get()
    (
        device_timestamp,
        device_id,
        data,
        stop,
        impedance,
    ) = unpack_from_queue(package)

    if data is not None:
        data_model.payload = data
    if device_timestamp is not None:
        data_model.deviceTimestamp = device_timestamp
    if device_id is not None:
        data_model.deviceID = device_id
    if stop is not None:
        data_model.stop = stop
    if impedance is not None:
        data_model.impedance = impedance
    return data_model, data_queue
