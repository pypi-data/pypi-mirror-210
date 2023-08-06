import logging

log = logging.getLogger(__name__)


def get_layer_from_serial_number(serial_number):
    """
    Get the layer from the serial number.
    """
    if len(serial_number) != 14 or not serial_number.startswith("20U"):
        log.exception("Error: Please enter a valid ATLAS SN.")
        raise ValueError()

    if "PIMS" in serial_number or "PIR6" in serial_number:
        return "L0"

    if "PIM0" in serial_number or "PIR7" in serial_number:
        return "R0"

    if "PIM5" in serial_number or "PIR8" in serial_number:
        return "R0.5"

    if "PIM1" in serial_number or "PIRB" in serial_number:
        return "L1"

    if "PG" in serial_number:
        return "L2"

    log.exception("Error: invalid module SN.")
    raise ValueError()


def chip_serial_number_to_uid(serial_number):
    """
    Convert chip serial number to hexadecimal UID.
    """
    assert serial_number.startswith(
        "20UPGFC"
    ), "Serial number must be for a valid RD53B"
    return hex(int(serial_number[-7:]))


def chip_uid_to_serial_number(uid):
    """
    Convert chip hexadecimal UID to serial number.
    """
    return f"20UPGFC{int(uid, 16):07}"
