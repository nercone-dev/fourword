# FourWord
A new random identifier generation method capable of chronological sorting

## Overview
This is a new method for generating random identifiers.
It is designed for use as primary keys in databases and similar applications.

It includes a timestamp at the beginning and uses Base32 Hex as the character set for text conversion, allowing for sorting in chronological order.
Since Z is used instead of = for padding, it should be usable anywhere alphanumeric characters are supported.

To minimize the possibility of collisions while also preventing overflow, the timestamp is not fixed but occupies 1/4 of the total bit length.
This means that simply increasing the total bit length increases the length of the timestamp, allowing for longer continuous usage.

However, a trade-off is that increasing the bit length results in unnecessary leading zeros in the timestamp section.

## Etymology
The "Four" in the name comes from the fact that the timestamp occupies 1/4 of the bit length.
It is also a play on the word "Forward."

## Python Library
```sh
# Install using pip
pip3 install fourword

# Install using uv
uv pip install fourword

# Add to Project using uv
uv add fourword
```

```python
from fourword.lib import FourWord

fourword = FourWord(bits=256)
print(fourword.text)
print(fourword.timestamp.isoformat())
```

```sh
# Show usage
fourword --help
# Generate FourWord ID with default(256) bits
fourword g
# Generate FourWord ID with custom 512 bits
fourword g --bits 512
# Generate FourWord ID and Show with details
fourword g --verbose
# Decode FourWord ID and Show with details
fourword i 32OD9FEO1M8G0I7A0CMGMC599N14NJQ9SQAJPT3TRATETRAMBKTGZZZZ
```

You can generate and analyze FourWord using the fourword library in Python.
The Python library also includes a fourword CLI tool.

## Specifications
FourWord is represented as the following byte sequence (big-endian):

```
[ (Total bits/4) bit UNIX timestamp (UTC, ns) ] + [ (Total bits/4*3) bit CSPRNG ]
```

For example, when the total bit length is 256 bits, the timestamp is 64 bits and the random part is 192 bits.

The ratio is fixed so that when retrieving the timestamp from an ID, the exact length can be easily determined without needing a separator.

Unlike other methods such as UUID, FourWord does not strictly require text conversion. It supports both byte sequence and text formats.

### Numericalization
Numericalization is simply a matter of interpreting the byte sequence as a binary number and converting it to decimal.

### Text Conversion
Text conversion uses a variant of Base32 Hex.

As mentioned above, Z is used instead of = as the padding character, but otherwise, it is identical to Base32 Hex.

### Collision Probability
IDs with different timestamps do not collide. The values below represent the worst-case scenario (all IDs generated within the same nanosecond).

| Bits | Random bit width | IDs for 10⁻¹⁸ collision prob. | IDs for 10⁻⁹ collision prob. | IDs for 50% collision prob. |
|---:|---:|:---|:---|:---|
| 256 | 192 bit | approx 1.12 × 10²⁰ | approx 3.54 × 10²⁴ | approx 9.33 × 10²⁸ |
| 512 | 384 bit | approx 8.88 × 10⁴⁸ | approx 2.81 × 10⁵³ | approx 7.39 × 10⁵⁷ |
| 768 | 576 bit | approx 7.03 × 10⁷⁷ | approx 2.22 × 10⁸² | approx 5.85 × 10⁸⁶ |
| 1024 | 768 bit | approx 5.57 × 10¹⁰⁶ | approx 1.76 × 10¹¹¹ | approx 4.64 × 10¹¹⁵ |
| 1280 | 960 bit | approx 4.41 × 10¹³⁵ | approx 1.40 × 10¹⁴⁰ | approx 3.67 × 10¹⁴⁴ |
| 1536 | 1152 bit | approx 3.50 × 10¹⁶⁴ | approx 1.11 × 10¹⁶⁹ | approx 2.91 × 10¹⁷³ |
| 1792 | 1344 bit | approx 2.77 × 10¹⁹³ | approx 8.76 × 10¹⁹⁷ | approx 2.31 × 10²⁰² |
| 2048 | 1536 bit | approx 2.20 × 10²²² | approx 6.94 × 10²²⁶ | approx 1.83 × 10²³¹ |

### Overflow Timing
Each bit length will overflow at the following times:

| Bits | Timestamp bit width | Max seconds | Overflow timing (approx) |
|---:|---:|:---|:---|
| 256 | 64 bit | approx 1.84 × 10¹⁹ s | approx 584.4 billion years AD (5.845 × 10¹¹ years) |
| 512 | 128 bit | approx 3.40 × 10³⁸ s | approx 1.07 × 10³¹ years later |
| 768 | 192 bit | approx 6.28 × 10⁵⁷ s | approx 1.99 × 10⁵⁰ years later |
| 1024 | 256 bit | approx 1.16 × 10⁷⁷ s | approx 3.67 × 10⁶⁹ years later |
| 1280 | 320 bit | approx 2.14 × 10⁹⁶ s | approx 6.77 × 10⁸⁸ years later |
| 1536 | 384 bit | approx 3.94 × 10¹¹⁵ s | approx 1.25 × 10¹⁰⁸ years later |
| 1792 | 448 bit | approx 7.26 × 10¹³⁴ s | approx 2.30 × 10¹²⁷ years later |
| 2048 | 512 bit | approx 1.34 × 10¹⁵⁴ s | approx 4.24 × 10¹⁴⁶ years later |

## License
The source code and library within this repository are free to use under the MIT License.

Credit is not required for software that utilizes the FourWord specification itself or for data generated using FourWord.
