#!/usr/bin/env python3
import argparse
from pathlib import Path

def check_path(path_str):
    path = Path(path_str)
    if path.exists():
        if path.is_file():
            print(f"'{path}' 存在，并且是一个文件")
        elif path.is_dir():
            print(f"'{path}' 存在，并且是一个目录")
        else:
            print(f"'{path}' 存在，但不是文件或目录")
    else:
        print(f"'{path}' 不存在")

def main():
    parser = argparse.ArgumentParser(description="检查路径是否存在")
    parser.add_argument("--path", help="要检查的路径")
    args = parser.parse_args()

    check_path(args.path)

if __name__ == "__main__":
    main()
