#!/usr/bin/env python3

import argparse
import subprocess

from pathlib import Path


def generate_python_protobufs(proto_dir: Path, py_out_dir: Path):
    print("Generating Python protobufs...")
    proto_files = list(proto_dir.rglob("*.proto"))
    subprocess.run([
        "protoc",
        f"--proto_path={proto_dir}",
        f"--python_betterproto_out={py_out_dir}",
        *map(str, proto_files)
    ], check=True)


def generate_ts_protobufs(proto_dir: Path, ts_out_dir: Path):
    print("Generating TypeScript protobufs...")

    plugin_path = Path("./frontend/node_modules/.bin/protoc-gen-ts_proto").resolve()

    if not plugin_path.exists():
        raise FileNotFoundError(f"Plugin not found: {plugin_path}")

    proto_files = list(proto_dir.rglob("*.proto"))
    subprocess.run([
        "protoc",
        f"--proto_path={proto_dir}",
        f"--plugin=protoc-gen-ts_proto={plugin_path}",
        f"--ts_proto_out={ts_out_dir}",
        *map(str, proto_files)
    ], check=True)


def main():
    parser = argparse.ArgumentParser(description="Generate Python and TypeScript protobufs.")
    parser.add_argument("--proto_dir", type=Path, required=True, help="Directory containing .proto files")
    parser.add_argument("--py_out", type=Path, required=True, help="Python output directory")
    parser.add_argument("--ts_out", type=Path, required=True, help="TypeScript output directory")
    args = parser.parse_args()

    generate_python_protobufs(args.proto_dir, args.py_out)
    generate_ts_protobufs(args.proto_dir, args.ts_out)
    print("Protobuf generation complete.")


if __name__ == "__main__":
    main()
