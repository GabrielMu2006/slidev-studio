#!/usr/bin/env python3
"""Create a new Slidev example project without installing or overwriting files."""

import argparse
import json
from pathlib import Path
import re
import shutil
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--title", default="Make the mechanism visible")
    parser.add_argument("--lang", default="en")
    parser.add_argument("--slidev-version", default="53.0.0",
                        help="Verified exact CLI release (default: 53.0.0)")
    args = parser.parse_args()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", args.slidev_version):
        parser.error("--slidev-version must be an exact semantic version")
    if not re.fullmatch(r"[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*", args.lang):
        parser.error("--lang must be a language tag such as en or zh-CN")
    if not args.title.strip():
        parser.error("--title cannot be blank")

    source = Path(__file__).resolve().parent.parent / "assets" / "starter"
    destination = args.destination.expanduser().absolute()
    if not source.is_dir():
        parser.error(f"starter assets missing: {source}")
    try:
        # Also refuses an existing empty directory or a symlink.
        destination.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        parser.error(f"destination already exists; no files changed: {destination}")
    try:
        shutil.copytree(source, destination, dirs_exist_ok=True)
        slides = destination / "slides.md"
        content = slides.read_text(encoding="utf-8")
        content = content.replace("__TITLE_JSON__", json.dumps(args.title, ensure_ascii=False))
        content = content.replace("__LANG_JSON__", json.dumps(args.lang))
        slides.write_text(content, encoding="utf-8")
        package = {
            "name": "slidev-talk",
            "private": True,
            "type": "module",
            "scripts": {"dev": "slidev", "build": "slidev build", "export": "slidev export"},
            "devDependencies": {
                "@slidev/cli": args.slidev_version,
                "@slidev/theme-default": "0.25.0",
                "vue": "^3.5.0",
            },
        }
        if args.slidev_version == "53.0.0":
            package["engines"] = {"node": ">=22.12.0"}
        (destination / "package.json").write_text(
            json.dumps(package, indent=2) + "\n", encoding="utf-8")
    except Exception:
        # Only this invocation's newly created directory is removed on failure.
        shutil.rmtree(destination)
        raise
    print(f"Created {destination}")
    print("Next: install dependencies with the project's package manager, then run dev and build.")
    print("Rewrite the sample narrative for the audience; inspect slides before delivery.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
