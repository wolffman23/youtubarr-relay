from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dispatcharr_plugin" / "youtubarr_relay"
FIXED_TIMESTAMP = (2026, 1, 1, 0, 0, 0)


def build(output: Path) -> None:
    files = sorted(path for path in SOURCE.rglob("*") if path.is_file())
    if {path.name for path in files} != {"plugin.py", "plugin.json"}:
        raise ValueError("plugin source must contain only manifest and entry point")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            info = zipfile.ZipInfo(f"youtubarr_relay/{path.name}", date_time=FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    print(f"built {output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "youtubarr-relay-plugin.zip")
    args = parser.parse_args()
    build(args.output)


if __name__ == "__main__":
    main()
