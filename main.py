#!/usr/bin/env python3
"""news-image-20261123 v1 entrypoint: copy the prebuilt entry.png to the
grader's output directory. Standard library only, deterministic.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    with open(dst, "rb") as f:
        data = f.read()
    assert len(data) <= 1048576, f"entry.png is {len(data)} bytes, over 1 MiB"
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "entry.png is not a PNG"
    print(f"entry.png: {len(data)} bytes, "
          f"sha256 {hashlib.sha256(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
