import hashlib


def base58(address_hex):
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    b58_string = ''
    # Get the number of leading zeros
    leading_zeros = len(address_hex) - len(address_hex.lstrip('0'))
    # Convert hex to decimal
    address_int = int(address_hex, 16)
    # Append digits to the start of string
    while address_int > 0:
        digit = address_int % 58
        digit_char = alphabet[digit]
        b58_string = digit_char + b58_string
        address_int //= 58
    # Add ‘1’ for each 2 leading zeros
    ones = leading_zeros // 2
    for one in range(ones):
        b58_string = '1' + b58_string
    return b58_string

def genaddr(pubkey, net):
    if net not in ("testnet", "mainnet"):
        raise ValueError("net must be testnet or mainnet")
    addr = hashlib.sha256(pubkey).digest()
    ripemd160 = hashlib.new("ripemd160")
    ripemd160.update(addr)
    addr = ripemd160.digest()
    netprefix = b'\x6f' if net == "testnet" else b'\x00'
    addr = netprefix + addr
    checksum = hashlib.sha256(addr).digest()
    checksum = hashlib.sha256(checksum).digest()
    checksum = checksum[:4]
    addr = addr + checksum
    return base58(addr.hex())