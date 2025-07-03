#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from pathlib import Path
from shutil import rmtree
from typing import List


class Protoc:
    # make sure to pull deps first, especially with npm
    __base_command_name = "protoc"
    __ts_plugin_path = Path("frontend/node_modules/.bin")
    __py_plugin_path = Path(".venv/bin")

    @classmethod
    def collect_files(cls, proto_dir: Path = Path.cwd()) -> List[Path]:
        return list(proto_dir.rglob("*.proto"))

    @classmethod
    def invoke(cls, output_param: str, output_dir: str):
        path = os.environ["PATH"]
        env = {
            "PATH": f"{path}:{cls.__ts_plugin_path}:{cls.__py_plugin_path}",
        }

        result = subprocess.run(
            [cls.__base_command_name, f"--{output_param}={output_dir}", f"--proto_path={Path.cwd()}", *cls.collect_files()],
            env=os.environ.update(env),
        )

        if result.returncode:
            sys.exit(result.returncode)


def clean_output_dir(output_dir: Path):
    if not output_dir.is_dir():
        return

    for dir, dirs, files in output_dir.walk():
        for file in files:
            if file == ".gitkeep":
                continue

            (dir / file).unlink()

        for folded_dir in dirs:
            rmtree(dir / folded_dir)


def main():
    parser = argparse.ArgumentParser(description="Generate Python and TypeScript protobufs.")
    parser.add_argument("--proto_dir", type=Path, default=Path.cwd(), help="Directory containing .proto files (default: current directory)")
    parser.add_argument("--py_out", action="store", help="Python output directory")
    parser.add_argument("--ts_out", action="store", help="TypeScript output directory")
    args = parser.parse_args()

    if args.ts_out is not None:
        clean_output_dir(Path(args.ts_out))
        Protoc.invoke("ts_proto_out", Path(args.ts_out))
    if args.py_out is not None:
        clean_output_dir(Path(args.py_out))
        Protoc.invoke("python_betterproto_out", Path(args.py_out))


if __name__ == "__main__":
    main()
