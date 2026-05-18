import sys
import warnings
import argparse

from .lib import FourWord

base32_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUV"
base32_map = {c: i for i, c in enumerate(base32_chars)}

def _text_to_bytes(text: str) -> bytes:
    stripped = text.rstrip("Z")
    value = 0
    for ch in stripped:
        if ch not in base32_map:
            raise ValueError(f"Invalid character in FourWord ID: {ch!r}")
        value = (value << 5) | base32_map[ch]
    total_bits = len(stripped) * 5
    pad = total_bits % 8
    value >>= pad
    byte_len = (total_bits - pad) // 8
    return value.to_bytes(byte_len, "big")

def _extract_timestamp(raw: bytes, bits: int) -> int:
    ts_bytes = bits // 4 // 8
    return int.from_bytes(raw[:ts_bytes], "big")

def _format_output(fw: FourWord, fmt: str) -> str | bytes:
    match fmt:
        case "text":
            return fw.text
        case "hex":
            return fw.generated.hex()
        case "base64":
            import base64
            return base64.b64encode(fw.generated).decode()
        case "int":
            return str(int.from_bytes(fw.generated, "big"))
        case "bytes":
            return fw.generated
        case "all":
            import base64
            ts_ns = _extract_timestamp(fw.generated, fw.bits)
            ts_s = ts_ns / 1e9
            from datetime import datetime, timezone
            dt = datetime.fromtimestamp(ts_s, tz=timezone.utc).isoformat()
            lines = [
                f"text   : {fw.text}",
                f"hex    : {fw.generated.hex()}",
                f"base64 : {base64.b64encode(fw.generated).decode()}",
                f"int    : {int.from_bytes(fw.generated, 'big')}",
                f"bits   : {fw.bits}",
                f"bytes  : {len(fw.generated)}",
                f"ts_ns  : {ts_ns}",
                f"ts_utc : {dt}",
            ]
            return "\n".join(lines)
        case _:
            raise ValueError(f"Unknown format: {fmt}")

def cmd_generate(args: argparse.Namespace) -> int:
    with warnings.catch_warnings():
        if args.no_warn:
            warnings.simplefilter("ignore")
        else:
            warnings.simplefilter("always")

        sep = args.separator if args.separator is not None else "\n"

        outputs = []
        for _ in range(args.count):
            fw = FourWord(bits=args.bits)
            result = _format_output(fw, args.format)

            if args.format == "bytes":
                sys.stdout.buffer.write(result)
            else:
                outputs.append(result)

        if args.format != "bytes":
            print(sep.join(outputs))

    return 0

def cmd_inspect(args: argparse.Namespace) -> int:
    import base64
    from datetime import datetime, timezone

    try:
        raw = _text_to_bytes(args.id)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    bits = len(raw) * 8
    ts_bytes = bits // 4 // 8
    ts_ns = int.from_bytes(raw[:ts_bytes], "big")

    ns_2000 = 946_684_800_000_000_000
    ns_2100 = 4_102_444_800_000_000_000
    ts_valid = ns_2000 <= ts_ns <= ns_2100

    ts_s = ts_ns / 1e9
    dt = (
        datetime.fromtimestamp(ts_s, tz=timezone.utc).isoformat()
        if ts_valid
        else "(out of plausible range)"
    )

    random_part = raw[ts_bytes:]

    print(f"input    : {args.id}")
    print(f"hex      : {raw.hex()}")
    print(f"base64   : {base64.b64encode(raw).decode()}")
    print(f"bits     : {bits}")
    print(f"bytes    : {len(raw)}")
    print(f"ts_bytes : {ts_bytes}  ({ts_bytes * 8} bits, 1/4 of total)")
    print(f"rnd_bytes: {len(random_part)}  ({len(random_part) * 8} bits, 3/4 of total)")
    print(f"ts_ns    : {ts_ns}")
    print(f"ts_utc   : {dt}")
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fourword",
        description="FourWord — timestamp-prefixed, CSPRNG-backed ID generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  fourword                          generate one 256-bit ID (text)
  fourword -n 5                     generate 5 IDs
  fourword --bits 128               128-bit ID
  fourword --format hex             hex output
  fourword --format all             show all representations
  fourword -n 3 --separator ,       comma-separated IDs
  fourword inspect <ID>             decode and inspect a text ID
""",
    )

    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser(
        "generate",
        aliases=["gen"],
        help="generate one or more FourWord IDs (default command)",
    )
    _add_generate_args(gen)

    ins = sub.add_parser(
        "inspect",
        aliases=["info"],
        help="decode and inspect an existing FourWord text ID",
    )
    ins.add_argument("id", metavar="ID", help="FourWord text ID to inspect")

    _add_generate_args(parser)

    return parser

def _add_generate_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--bits", "-b",
        type=int,
        default=256,
        metavar="N",
        help="number of bits (must be divisible by 32, default: 256)",
    )
    p.add_argument(
        "--count", "-n",
        type=int,
        default=1,
        metavar="N",
        help="number of IDs to generate (default: 1)",
    )
    p.add_argument(
        "--format", "-f",
        choices=["text", "hex", "base64", "int", "bytes", "all"],
        default="text",
        metavar="FMT",
        help="output format: text|hex|base64|int|bytes|all (default: text)",
    )
    p.add_argument(
        "--separator", "-s",
        metavar="SEP",
        default=None,
        help="separator between IDs (default: newline)",
    )
    p.add_argument(
        "--no-warn",
        action="store_true",
        help="suppress warnings about non-32-divisible bit lengths",
    )

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command in ("inspect", "info"):
        return cmd_inspect(args)

    if args.command in ("generate", "gen", None):
        return cmd_generate(args)

    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main())
