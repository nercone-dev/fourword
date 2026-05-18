import time
import secrets
import warnings
import functools

class FourWord:
    def __init__(self, bits: int = 256):
        self.bits = bits
        self.generate()

    def generate(self, bits: int | None = None) -> bytes:
        if bits:
            self.bits = bits

        if self.bits % 32 != 0:
            warnings.warn("The number of bits is not divisible by 32. The actual generated length may not match the number of bits.", BytesWarning, stacklevel=2)

        timestamp_bits = self.bits // 4
        csprng_bits = (self.bits // 4) * 3

        time_ns = time.time_ns()
        try:
            timestamp = time_ns.to_bytes(timestamp_bits // 8, byteorder='big')

        except OverflowError:
            bytes_needed = ((time_ns.bit_length() + 7) // 8) * 4
            bits_needed = bytes_needed * 8
            raise OverflowError(f"bits must be >= {bits_needed} (timestamp requires {time_ns.bit_length()}-bit minimum)")

        random = secrets.token_bytes(int(csprng_bits / 8))

        self.generated = timestamp + random
        return self.generated

    @functools.cached_property
    def text(self) -> str:
        chars = b"0123456789ABCDEFGHIJKLMNOPQRSTUV"
        result = []
        bits = int.from_bytes(self.generated, "big")
        bit_len = len(self.generated) * 8

        pad = (5 - bit_len % 5) % 5
        bits <<= pad
        bit_len += pad

        for _ in range(bit_len // 5):
            bit_len -= 5
            result.append(chars[(bits >> bit_len) & 0x1F])

        pad_len = (8 - len(result) % 8) % 8
        return bytes(result).decode('ascii') + "Z" * pad_len

    @property
    def bytes(self) -> bytes:
        return self.generated
