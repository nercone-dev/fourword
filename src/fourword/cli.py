import sys
import argparse
from datetime import datetime, timezone
from .lib import FourWord

def parse_iso8601(s: str) -> datetime:
    try:
        dt = datetime.fromisoformat(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        print(f"Error: Invalid datetime format: {s}", file=sys.stderr)
        print("Use ISO 8601 format, e.g. 2024-01-01T00:00:00+09:00", file=sys.stderr)
        sys.exit(1)

def print_fourword(fw: FourWord, detail: bool = False) -> None:
    if detail:
        print(f"Text     : {fw.text}")
        print(f"Compact  : {fw.compact_text}")
        print(f"Readable : {fw.readable_text}")
        print(f"Decimal  : {fw.decimal}")
        print(f"Hex      : {fw.hex}")
        print(f"Bits     : {fw.bits}")
        print(f"Timestamp: {fw.timestamp.isoformat()}")
        print(f"Unix (ns): {int(fw.timestamp.timestamp() * 1_000_000_000)}")
        print(f"Unix (ms): {int(fw.timestamp.timestamp() * 1_000)}")
    else:
        print(fw.text)

def is_bit_size(s: str) -> bool:
    try:
        n = int(s)
        return n % 32 == 0 and 32 <= n <= 65536
    except ValueError:
        return False

def cmd_generate(args):
    dt = parse_iso8601(args.timestamp) if args.timestamp else None
    for i in range(args.nums):
        if i > 0 and args.detail:
            print()
        try:
            fw = FourWord(args.bits, dt)
        except OverflowError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        print_fourword(fw, args.detail)

def cmd_info(args):
    for i, id_str in enumerate(args.id):
        if i > 0:
            print()
        try:
            fw = FourWord(id_str)
        except Exception as e:
            print(f"Error: Failed to parse FourWord '{id_str}': {e}", file=sys.stderr)
            sys.exit(1)
        print_fourword(fw, detail=True)

def cmd_default(args):
    values = args.values or []
    to_decode = [v for v in values if not is_bit_size(v)]
    to_generate = [int(v) for v in values if is_bit_size(v)]

    dt = parse_iso8601(args.timestamp) if args.timestamp else None

    if not to_generate and not to_decode:
        to_generate = [FourWord.min_bits(dt)]

    for bits in to_generate:
        for i in range(args.nums):
            try:
                fw = FourWord(bits, dt)
            except OverflowError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
            print_fourword(fw, args.detail)
            if args.detail and i < (args.nums - 1):
                print()

    for i in range(len(to_decode)):
        try:
            fw = FourWord(to_decode[i])
        except Exception as e:
            print(f"Error: Failed to parse FourWord '{to_decode[i]}': {e}", file=sys.stderr)
            sys.exit(1)
        print_fourword(fw, detail=True)
        if args.detail and i < (args.nums - 1):
            print()

def main():
    if len(sys.argv) == 1 or not sys.argv[1] in ['generate', 'gen', 'g', 'info', 'show', 'i']:
        parser = argparse.ArgumentParser(prog="fourword")
        parser.add_argument("values", nargs="*", metavar="VALUE", help="Bit sizes (32–65536, ×32) to generate, or FourWord IDs to decode")
        parser.add_argument("--timestamp", "-t", "--datetime", type=str, default=None, metavar="ISO8601")
        parser.add_argument("--detail", "-d", "--verbose", "-v", action="store_true")
        parser.add_argument("--nums", "-n", type=int, default=1, metavar="N")
        args = parser.parse_args()
        args.command = None
        cmd_default(args)
        return

    parser = argparse.ArgumentParser(prog="fourword")
    command = parser.add_subparsers(dest="command")

    generate = command.add_parser("generate", aliases=["gen", "g"], help="Generate a new FourWord ID")
    generate.add_argument("--bits", "-b", type=int, default=None, metavar="N", help="Bit size (multiple of 32, default: 256)")
    generate.add_argument("--timestamp", "-t", "--datetime", type=str, default=None, metavar="ISO8601", help="Timestamp to embed (ISO 8601, default: now)")
    generate.add_argument("--detail", "-d", "--verbose", "-v", action="store_true", help="Show all formats")
    generate.add_argument("--nums", "-n", type=int, default=1, metavar="N", help="Number of IDs to generate")
    generate.set_defaults(func=cmd_generate)

    info = command.add_parser("info", aliases=["show", "i"], help="Decode and show FourWord info")
    info.add_argument("id", type=str, nargs="+", help="FourWord ID(s) to decode")
    info.set_defaults(func=cmd_info)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
