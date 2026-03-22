#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from libswzl2 import encode, decode, inspect


def cmd_encode(args):
    try:
        encode(
            image_path=args.input,
            output_path=args.output,
            force_alpha=args.force_alpha
        )
    except Exception as e:
        print(f"[error] encode failed: {e}")
        sys.exit(1)


def cmd_decode(args):
    try:
        decode(
            swzl_path=args.input,
            output_path=args.output
        )
    except Exception as e:
        print(f"[error] decode failed: {e}")
        sys.exit(1)


def cmd_inspect(args):
    try:
        inspect(args.input)
    except Exception as e:
        print(f"[error] inspect failed: {e}")
        sys.exit(1)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="swzlr",
        description="Swizzler - The complete SWZL CLI toolkit"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- encode ---
    p_encode = subparsers.add_parser(
        "encode",
        help="Encode an image into .swzl format"
    )
    p_encode.add_argument("input", help="Input image path (png, jpg, etc.)")
    p_encode.add_argument("output", help="Output .swzl file")
    p_encode.add_argument(
        "-a", "--force-alpha",
        action="store_true",
        help="Force RGBA encoding even if input has no alpha"
    )
    p_encode.set_defaults(func=cmd_encode)

    # --- decode ---
    p_decode = subparsers.add_parser(
        "decode",
        help="Decode a .swzl file into an image"
    )
    p_decode.add_argument("input", help="Input .swzl file")
    p_decode.add_argument("output", help="Output image (png recommended)")
    p_decode.set_defaults(func=cmd_decode)

    # --- inspect ---
    p_inspect = subparsers.add_parser(
        "inspect",
        help="Inspect a .swzl file without decoding"
    )
    p_inspect.add_argument("input", help="Input .swzl file")
    p_inspect.set_defaults(func=cmd_inspect)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # basic sanity checks
    if hasattr(args, "input") and not Path(args.input).exists():
        print(f"[error] Input file not found: {args.input}")
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
