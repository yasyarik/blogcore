#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

from reel_voiceover_library import build_reel_voiceover_catalog


def main():
    parser = argparse.ArgumentParser(description="Build a non-destructive library of complete Reel voiceovers.")
    parser.add_argument("site_id", type=int)
    parser.add_argument("--base-dir", default=str(Path(__file__).resolve().parent))
    args = parser.parse_args()
    base_dir = Path(args.base_dir).resolve()
    catalog = build_reel_voiceover_catalog(
        base_dir / "data" / "social_assets" / str(args.site_id),
        base_dir / "data" / "reel_asset_library",
        args.site_id,
        base_dir / "data" / "blog_core.sqlite3",
    )
    print(json.dumps(catalog["summary"], ensure_ascii=False, sort_keys=True))
    print(Path(catalog["libraryRoot"]).parent / "voiceovers.json")


if __name__ == "__main__":
    main()
