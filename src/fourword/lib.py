import math
import secrets
import warnings
from datetime import datetime, timezone

class FourWord:
    def __init__(self, arg: str | bytes | int | None = None, dt: datetime | None = None):
        if arg is None:
            self.bytes = self.generate(dt=dt)
        elif isinstance(arg, str):
            detected_format = FourWord.detect_format(arg)
            if detected_format == 'readable':
                self.bytes = FourWord.from_readable_text(arg).bytes
            elif detected_format == 'compact':
                self.bytes = FourWord.from_compact_text(arg).bytes
            elif detected_format == 'decimal':
                self.bytes = FourWord.from_decimal(arg).bytes
            elif detected_format == 'hex':
                self.bytes = FourWord.from_hex(arg).bytes
            else:
                self.bytes = FourWord.from_text(arg).bytes
        elif isinstance(arg, bytes):
            self.bytes = arg
        elif isinstance(arg, int):
            if arg % 32 == 0 and 32 <= arg <= 65536:
                self.bytes = self.generate(arg, dt)
            else:
                self.bytes = FourWord.from_decimal(arg).bytes

    @staticmethod
    def detect_format(text: str) -> str:
        if not text:
            return 'text'
        if '-' in text:
            return 'readable'
        if text.isdigit():
            return 'decimal'

        has_upper = any(c.isupper() for c in text)
        has_lower = any(c.islower() for c in text)

        if (has_upper and has_lower) or any(c in 'WXYwxyz' for c in text):
            return 'compact'
        if has_lower and all(c in '0123456789abcdef' for c in text):
            return 'hex'
        if has_lower:
            return 'readable'

        return 'text'

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

    @staticmethod
    def from_compact_text(text: str) -> "FourWord":
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        bits = round(len(text) / (math.log(2) / math.log(62)) / 32) * 32
        byte_len = bits // 8
        n = 0
        for c in text:
            n = n * 62 + chars.index(c)
        return FourWord.from_decimal(n, bits)

    @staticmethod
    def from_readable_text(text: str) -> "FourWord":
        clean = text.replace('-', '').upper()
        pad = (8 - len(clean) % 8) % 8
        return FourWord.from_text(clean + 'Z' * pad)

    @staticmethod
    def from_decimal(value: int | str, bits: int | None = None) -> "FourWord":
        n = int(value)
        if bits is None:
            bits = n.bit_length() - 1
        raw = n - (1 << bits)
        return FourWord(raw.to_bytes(bits // 8, 'big'))

    @staticmethod
    def from_hex(text: str) -> "FourWord":
        raw = bytes.fromhex(text)
        return FourWord(raw)

    @staticmethod
    def min_bits(dt: datetime | None = None) -> int:
        if dt is not None:
            if dt.tzinfo is not None:
                dt_utc = dt
            else:
                dt_utc = dt.replace(tzinfo=timezone.utc)
        else:
            dt_utc = datetime.now(timezone.utc)

        time_ns = int(dt_utc.timestamp() * 1_000_000_000)
        return ((time_ns.bit_length() + 7) // 8) * 32

    def generate(self, bits: int | None = None, dt: datetime | None = None) -> bytes:
        if bits is None:
            bits = FourWord.min_bits(dt)

        min_bits = FourWord.min_bits(dt)
        if bits < min_bits:
            raise OverflowError(f"bits must be >= {min_bits} (timestamp requires {min_bits // 4}-bit minimum)")

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

        timestamp = time_ns.to_bytes(bits_timestamp // 8, byteorder='big')
        csprng = secrets.token_bytes(int(bits_csprng / 8))

        return timestamp + csprng

    @property
    def bits(self) -> int:
        return len(self.bytes) * 8

    @property
    def bits_timestamp(self) -> int:
        return self.bits // 4

    @property
    def bits_csprng(self) -> int:
        return (self.bits // 4) * 3

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
    def compact_text(self) -> str:
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        n = int.from_bytes(self.bytes, 'big')
        length = math.ceil(len(self.bytes) * 8 * (math.log(2) / math.log(62)))
        result = []
        while n:
            result.append(chars[n % 62])
            n //= 62
        while len(result) < length:
            result.append('0')
        return ''.join(reversed(result))

    @property
    def readable_text(self) -> str:
        raw = self.text.rstrip('Z').lower()
        return '-'.join(raw[i:i+8] for i in range(0, len(raw), 8))

    @property
    def decimal(self) -> int:
        n = len(self.bytes) * 8
        return (1 << n) + int.from_bytes(self.bytes, 'big')

    @property
    def hex(self) -> str:
        return self.bytes.hex()

    def __str__(self) -> str:
        return self.text

    def __int__(self) -> int:
        return self.decimal
