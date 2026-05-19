import secrets
import warnings
from datetime import datetime, timezone

class FourWord:
    def __init__(self, arg: str | bytes | int | None = 256, dt: datetime | None = None):
        self.bytes = None
        if isinstance(arg, str):
            self.bytes = FourWord.from_text(arg).bytes
        elif isinstance(arg, bytes):
            self.bytes = arg
        elif isinstance(arg, int):
            self.bytes = self.generate(arg, dt)

    @staticmethod
    def from_text(text: str) -> "FourWord":
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUV"
        text = text.rstrip('Z')
        bits_val = 0
        for c in text:
            bits_val = (bits_val << 5) | chars.index(c)
        total_bits = len(text) * 5
        byte_len = total_bits // 8
        bits_val >>= total_bits % 8
        return FourWord(bits_val.to_bytes(byte_len, 'big'))

    def generate(self, bits: int = 256, dt: datetime | None = None) -> bytes:
        if bits % 32 != 0:
            warnings.warn("The number of bits is not divisible by 32. The actual generated length may not match the number of bits.", UserWarning, stacklevel=2)

        if dt is not None:
            if dt.tzinfo is not None:
                dt_utc = dt
            else:
                dt_utc = dt.replace(tzinfo=timezone.utc)
        else:
            dt_utc = datetime.now(timezone.utc)

        time_ns = int(dt_utc.timestamp() * 1_000_000_000)

        bits_timestamp = bits // 4
        bits_csprng = (bits // 4) * 3

        try:
            timestamp = time_ns.to_bytes(bits_timestamp // 8, byteorder='big')
        except OverflowError:
            bits_needed = ((time_ns.bit_length() + 7) // 8) * 32
            raise OverflowError(f"bits must be >= {bits_needed} (timestamp requires {time_ns.bit_length()}-bit minimum)")

        random = secrets.token_bytes(int(bits_csprng / 8))
        return timestamp + random

    @property
    def timestamp(self) -> datetime:
        ts_byte_len = len(self.bytes) // 4
        time_ns = int.from_bytes(self.bytes[:ts_byte_len], byteorder='big')
        return datetime.fromtimestamp(time_ns / 1_000_000_000, tz=timezone.utc)

    @property
    def text(self) -> str:
        chars = b"0123456789ABCDEFGHIJKLMNOPQRSTUV"
        result = []
        bits = int.from_bytes(self.bytes, "big")
        bit_len = len(self.bytes) * 8

        pad = (5 - bit_len % 5) % 5
        bits <<= pad
        bit_len += pad

        for _ in range(bit_len // 5):
            bit_len -= 5
            result.append(chars[(bits >> bit_len) & 0x1F])

        pad_len = (8 - len(result) % 8) % 8
        return bytes(result).decode('ascii') + "Z" * pad_len

    @property
    def int(self) -> int:
        return int.from_bytes(self.bytes, 'big')

    @property
    def hex(self) -> str:
        return self.bytes.hex()
