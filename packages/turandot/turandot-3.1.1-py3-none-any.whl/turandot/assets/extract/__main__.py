import sys
import argparse
from pathlib import Path

from turandot.model.util import ModelUtils


def get_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="turandot.assets.extract",
        description="Turandot asset extractor"
    )
    ap.add_argument("-f", "--file", help="name of the file to extract")
    ap.add_argument("-d", "--destination", help="absolute path to extract the file to")
    return ap


if __name__ == "__main__":
    parser = get_arg_parser()
    args = parser.parse_args()
    try:
        file_bytes = ModelUtils.get_asset_bytes(args.file)
    except FileNotFoundError:
        print(f"ERROR: Not found in assets: {args.file}", file=sys.stderr)
        exit(1)
    target_path = Path(args.destination)
    if not target_path.is_absolute():
        print(f"ERROR: target must specify an absolute path", file=sys.stderr)
        exit(2)
    if not target_path.is_dir():
        print(f"ERROR: destination is not a directory", file=sys.stderr)
        exit(3)
    try:
        with (target_path / args.file).open("wb") as f:
            f.write(file_bytes)
    except PermissionError:
        print(f"ERROR: Writing permissions denied on {target_path}", file=sys.stderr)
        exit(4)
