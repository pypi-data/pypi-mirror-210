from typing import Optional

from eth_typing import HexAddress
from web3 import Web3

from .errors import InvalidAddressError


def to_bytes32(string: str) -> bytes:
    encoded_string = string.encode('utf-8')
    if len(encoded_string) > 32:
        raise ValueError("Input string is too long for bytes32")
    padding_length = 32 - len(encoded_string)
    padded_string = encoded_string + b'\x00' * padding_length
    return padded_string


def to_bytes(string: str) -> bytes:
    encoded_string = string.encode('utf-8')
    return encoded_string


def normalize_address(address: HexAddress) -> HexAddress:
    if len(address) == 42 or 40:
        return Web3.to_checksum_address(address)
    else:
        raise InvalidAddressError(f"{address} is invalid")
