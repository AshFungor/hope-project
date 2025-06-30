#!/usr/bin/env python3

import argparse
import subprocess
import sys
from pathlib import Path


def clean_output_dir(out_dir: Path):
    if not out_dir.exists():
        return

    for path in out_dir.iterdir():
        if path.name == ".gitkeep":
            continue
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            # Recursively delete directories
            for sub in path.rglob("*"):
                if sub.is_file():
                    sub.unlink()
                elif sub.is_dir():
                    try:
                        sub.rmdir()
                    except OSError:
                        pass
            try:
                path.rmdir()
            except OSError:
                pass


def generate_python_protobufs(proto_dir: Path, py_out_dir: Path):
    clean_output_dir(py_out_dir)

    proto_files = list(proto_dir.rglob("*.proto"))
    cmd = [
        "protoc",
        f"--proto_path={proto_dir}",
        f"--python_betterproto_out={py_out_dir}",
        *map(str, proto_files),
    ]

    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def generate_ts_protobufs(proto_dir: Path, ts_out_dir: Path):
    clean_output_dir(ts_out_dir)

    plugin_path = Path.cwd() / "frontend/node_modules/.bin/protoc-gen-ts_proto"

    proto_files = list(proto_dir.rglob("*.proto"))
    cmd = [
        "protoc",
        f"--proto_path={proto_dir}",
        f"--plugin=protoc-gen-ts_proto={plugin_path}",
        f"--ts_proto_out={ts_out_dir}",
        *map(str, proto_files),
    ]

    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="Generate Python and TypeScript protobufs.")
    parser.add_argument(
        "--proto_dir",
        type=Path,
        default=Path.cwd(),
        help="Directory containing .proto files (default: current directory)"
    )
    parser.add_argument("--py_out", action="store", help="Python output directory")
    parser.add_argument("--ts_out", action="store", help="TypeScript output directory")
    args = parser.parse_args()

    if args.py_out is not None:
        generate_python_protobufs(args.proto_dir, Path(args.py_out))
    if args.ts_out is not None:
        generate_ts_protobufs(args.proto_dir, Path(args.ts_out))
    print("Protobuf generation complete.")


if __name__ == "__main__":
    main()
