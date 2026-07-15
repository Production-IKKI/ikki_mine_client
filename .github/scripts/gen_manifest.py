#!/usr/bin/env python3
"""manifest.json 生成 (GitHub Actions 用)。

git 追跡ファイルを列挙し SHA-256 とサイズを記録する。
除外: .git* / .github/ / manifest.json 自身。
クライアントツールはこの manifest とローカルを比較して差分更新する。
URL は https://raw.githubusercontent.com/<owner>/<repo>/<commit>/<path>
(commit は本ファイル生成時の GITHUB_SHA にピン止め = アトミック性担保)。
"""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

EXCLUDE_PREFIXES = (".github/",)
EXCLUDE_FILES = {"manifest.json", ".gitignore", ".gitattributes"}


def main() -> int:
    files = subprocess.run(
        ["git", "ls-files", "-z"], capture_output=True, check=True
    ).stdout.decode("utf-8").split("\0")

    entries = {}
    for path in sorted(p for p in files if p):
        if path in EXCLUDE_FILES or path.startswith(EXCLUDE_PREFIXES):
            continue
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        entries[path] = {"sha256": h.hexdigest(), "size": os.path.getsize(path)}

    manifest = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commit": os.environ.get("GITHUB_SHA", "unknown"),
        "files": entries,
    }
    with open("manifest.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"manifest.json: {len(entries)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
