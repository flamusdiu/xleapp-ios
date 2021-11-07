def hexify_byte(byte_to_convert):
    to_return = hex(byte_to_convert).replace("0x", "")
    if len(to_return) < 2:
        to_return += "0"

    return to_return


def bytes_to_mac_address(encoded_bytes):
    return (
        f"{hexify_byte(encoded_bytes[0])}:{hexify_byte(encoded_bytes[1])}:"
        f"{hexify_byte(encoded_bytes[2])}:{hexify_byte(encoded_bytes[3])}:"
        f"{hexify_byte(encoded_bytes[4])}:{hexify_byte(encoded_bytes[5])}"
    )
