import sys
import argparse
from datetime import datetime, timezone
from .lib import FourWord

def cmd_generate(args):
    dt = None
    if args.datetime:
        try:
            dt = datetime.fromisoformat(args.datetime)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"Error: Invalid datetime format: {args.datetime}", file=sys.stderr)
            print("Use ISO 8601 format, e.g. 2024-01-01T00:00:00 or 2024-01-01T00:00:00+09:00", file=sys.stderr)
            sys.exit(1)

    for i in range(args.nums):
        try:
            fw = FourWord(args.bits, dt)
        except OverflowError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        if args.detail:
            print(f"Text     : {fw.text}")
            print(f"Compact  : {fw.compact_text}")
            print(f"Readable : {fw.readable_text}")
            print(f"Decimal  : {fw.int}")
            print(f"Hex      : {fw.hex}")
            print(f"Bits     : {args.bits}")
            print(f"Timestamp: {fw.timestamp.isoformat()}")
            print(f"Unix (ns): {int(fw.timestamp.timestamp() * 1_000_000_000)}")
            print(f"Unix (ms): {int(fw.timestamp.timestamp() * 1_000)}")
            if i + 1 < args.nums:
                print()
        else:
            print(fw.text)

def cmd_info(args):
    for i, id in enumerate(args.id):
        try:
            fw = FourWord(id)
        except (ValueError, Exception) as e:
            print(f"Error: Failed to parse FourWord '{id}': {e}", file=sys.stderr)
            sys.exit(1)

        print(f"Text     : {fw.text}")
        print(f"Compact  : {fw.compact_text}")
        print(f"Readable : {fw.readable_text}")
        print(f"Decimal  : {fw.int}")
        print(f"Hex      : {fw.hex}")
        print(f"Bits     : {len(fw.bytes) * 8}")
        print(f"Timestamp: {fw.timestamp.isoformat()}")
        print(f"Unix (ns): {int(fw.timestamp.timestamp() * 1_000_000_000)}")
        print(f"Unix (ms): {int(fw.timestamp.timestamp() * 1_000)}")
        if i + 1 < len(args.id):
            print()

def main():
    parser = argparse.ArgumentParser(prog="fourword", description="Generate and parse FourWord identifiers.")
    subparsers = parser.add_subparsers(dest="command", required=False)

    # generate
    generate = subparsers.add_parser("generate", aliases=["gen", "g"], help="Generate a new FourWord ID")
    generate.add_argument("--bits", "-b", type=int, default=256, metavar="N", help="Total bit size (must be divisible by 32, default: 256)")
    generate.add_argument("--datetime", "-d", type=str, default=None, metavar="ISO8601", help="Timestamp to embed (ISO 8601, default: now)")
    generate.add_argument("--detail", "--verbose", "-v", action="store_true", help="Show details")
    generate.add_argument("--nums", "-n", type=int, default=1, metavar="N", help="Number of IDs to generate (default: 1)")
    generate.set_defaults(func=cmd_generate)

    # info
    info = subparsers.add_parser("info", aliases=["show", "i"], help="Decode FourWord and Show informations")
    info.add_argument("id", type=str, nargs="+", help="FourWord text(s) to decode")
    info.set_defaults(func=cmd_info)

    args = parser.parse_args()

    if args.command is None:
        args.bits = 256
        args.datetime = None
        args.detail = False
        args.nums = 1
        args.func = cmd_generate

    args.func(args)

if __name__ == "__main__":
    main()
