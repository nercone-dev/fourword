# FourWord

## Overview
A new generation method for random identifiers.

It includes a timestamp at the beginning and uses Base32 Hex as the character set for text representation, allowing for sorting in chronological order.
Since 'Z' is used instead of '=' for padding, it should be usable in any environment that supports alphanumeric characters.

To minimize the possibility of collisions while preventing overflow, the timestamp is not fixed; instead, it occupies 1/4 of the total bits generated.
This allows for longer continuous use simply by increasing the total number of bits.
However, as a trade-off, unnecessary leading zeros will appear at the beginning of the timestamp portion.

It is intended for use in databases and similar applications.

## Etymology
The "Four" part comes from the fact that the timestamp occupies 1/4 of the total bits.
It is also a play on the word "Forward."

## Python Library
```
# Install using pip
pip3 install fourword

# Install using uv
uv pip install fourword

# Add to Project using uv
uv add fourword
```

```
from fourword.lib import FourWord

fourword = FourWord(bits=256)
print(fourword.text)
```

In Python, you can generate FourWord using the fourword library.
The fourword library works without any external dependencies.

The default bit size is 256.

The total number of bits must be divisible by 32.

## CLI Tool
There is a CLI tool that I had an AI create.
It hasn't been tested thoroughly, but it should work.

Once the library is installed, you should be able to use the `fourword-py` command.

## Specifications
A FourWord is represented as a byte sequence as follows:

```
[ (Total bits/4) bit UNIX timestamp (UTC, ns) ] + [ (Total bits/4*3) bit CSPRNG ]
```

For example, when the total bit size is 256 bits, the timestamp is 64 bits and the random part is 192 bits.

The ratio is fixed so that when retrieving the timestamp from an ID, the exact length can be easily determined without needing a separator.

Unlike other methods like UUID, FourWord does not require text representation. It supports both byte sequence and text formats.

### Text Representation
Text representation uses something similar to Base32 Hex.

As mentioned above, it uses 'Z' instead of '=' as a padding character, but otherwise, it is identical to Base32 Hex.

### Collision Probability
IDs with different timestamps will not collide. The values below are for the worst-case scenario (all IDs generated within the same nanosecond).

| Bits | Random Bit Width | IDs for 10⁻¹⁸ Collision Probability | IDs for 10⁻⁹ Collision Probability | IDs for 50% Collision Probability |
|---:|---:|:---|:---|:---|
| 256 | 192 bit | Approx. 1.12 × 10²⁰ | Approx. 3.54 × 10²⁴ | Approx. 9.33 × 10²⁸ |
| 512 | 384 bit | Approx. 8.88 × 10⁴⁸ | Approx. 2.81 × 10⁵³ | Approx. 7.39 × 10⁵⁷ |
| 768 | 576 bit | Approx. 7.03 × 10⁷⁷ | Approx. 2.22 × 10⁸² | Approx. 5.85 × 10⁸⁶ |
| 1024 | 768 bit | Approx. 5.57 × 10¹⁰⁶ | Approx. 1.76 × 10¹¹¹ | Approx. 4.64 × 10¹¹⁵ |
| 1280 | 960 bit | Approx. 4.41 × 10¹³⁵ | Approx. 1.40 × 10¹⁴⁰ | Approx. 3.67 × 10¹⁴⁴ |
| 1536 | 1152 bit | Approx. 3.50 × 10¹⁶⁴ | Approx. 1.11 × 10¹⁶⁹ | Approx. 2.91 × 10¹⁷³ |
| 1792 | 1344 bit | Approx. 2.77 × 10¹⁹³ | Approx. 8.76 × 10¹⁹⁷ | Approx. 2.31 × 10²⁰² |
| 2048 | 1536 bit | Approx. 2.20 × 10²²² | Approx. 6.94 × 10²²⁶ | Approx. 1.83 × 10²³¹ |

### Overflow Timeline
Overflow will occur at the following times for each bit size:

| Bits | Timestamp Bit Width | Max Seconds | Overflow Date (Approx.) |
|---:|---:|:---|:---|
| 256 | 64 bit | Approx. 1.84 × 10¹⁹ seconds | Approx. 584.4 billion years AD (5.845 × 10¹¹ years) |
| 512 | 128 bit | Approx. 3.40 × 10³⁸ seconds | Approx. 1.07 × 10³¹ years later |
| 768 | 192 bit | Approx. 6.28 × 10⁵⁷ seconds | Approx. 1.99 × 10⁵⁰ years later |
| 1024 | 256 bit | Approx. 1.16 × 10⁷⁷ seconds | Approx. 3.67 × 10⁶⁹ years later |
| 1280 | 320 bit | Approx. 2.14 × 10⁹⁶ seconds | Approx. 6.77 × 10⁸⁸ years later |
| 1536 | 384 bit | Approx. 3.94 × 10¹¹⁵ seconds | Approx. 1.25 × 10¹⁰⁸ years later |
| 1792 | 448 bit | Approx. 7.26 × 10¹³⁴ seconds | Approx. 2.30 × 10¹²⁷ years later |
| 2048 | 512 bit | Approx. 1.34 × 10¹⁵⁴ seconds | Approx. 4.24 × 10¹⁴⁶ years later |

## License
The source code and libraries in this repository are free to use under the MIT License.

Credit is not required for software that utilizes the FourWord specification itself or for data generated using FourWord.
