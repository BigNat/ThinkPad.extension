#!/usr/bin/env python3
"""
snapshot.py 🔨🤖🔧 – “snapshot_YYYY-MM-DD.txt” generator
------------------------------------------------------

• Walks only under THIS src directory (or a custom root)
• Stitches every .py / .json file into one text file
• Skips unwanted dirs/files (edit EXCLUDE_DIRS / DEFAULT_EXCLUDE)
• Verbose by default — pass  -q / --quiet  to mute per-file logging
"""

from __future__ import annotations
import argparse, datetime as _dt, fnmatch, sys, textwrap
from pathlib import Path

# ── CONFIG ───────────────────────────────────────────────────────────────────
EXCLUDE_DIRS = {"tools", "test_drivers", "$old", ".git", "__pycache__"}
DEFAULT_EXCLUDE = [
    "*.pyc", "*.log", "*copy*",             # file patterns
    "tools/**", "test_drivers/**", "*/$old/**",   # cross-OS folder patterns
    "*_code.txt", "*_snapshot.txt"
]
SKIP_FILENAMES = {"__init__.py", "___snapshot.py"}
ALLOWED_EXT  = {".py", ".json"}
HEADING_LINE = "#" * 80
# ─────────────────────────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create a source snapshot.")
    g = p.add_mutually_exclusive_group()
    g.add_argument("-q", "--quiet", action="store_true",
                   help="suppress per-file output")
    p.add_argument("-x", "--exclude", action="append", default=[],
                   help="additional glob to ignore (may repeat)")
    p.add_argument("-o", "--output", type=str, default=None,
                   help="custom output filename")
    p.add_argument("root", nargs="?",
                   default=str(Path(__file__).resolve().parent),
                   help="root dir (defaults to this script’s folder)")
    return p.parse_args()


# ── helper ───────────────────────────────────────────────────────────────────
def should_exclude(path: Path, patterns: list[str]) -> bool:
    """
    True if *path* should be skipped.
    • Skips anything whose *basename* is in SKIP_FILENAMES
    • Then tests the full path against the glob patterns (cross-OS)
    """
    if path.name in SKIP_FILENAMES:
        return True

    posix = path.as_posix()
    return any(fnmatch.fnmatch(posix, pat.replace("\\", "/"))
               for pat in patterns)


# ── scanner ──────────────────────────────────────────────────────────────────
def gather_files(root: Path, patterns: list[str], log: callable) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        # 1️⃣  hard-stop on blocked directories
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue

        # 2️⃣  file & glob checks
        if p.is_file() and p.suffix.lower() in ALLOWED_EXT \
           and not should_exclude(p, patterns):
            files.append(p)
            log(f"  + {p.relative_to(root)}")
    return sorted(files, key=lambda x: str(x).lower())


def build_snapshot(files: list[Path], root: Path) -> str:
    # ---- 1. index ----------------------------------------------------------
    index_lines = ["INDEX", "=" * 5, ""]
    index_lines.extend(str(f.relative_to(root)) for f in files)
    index_lines.append("─" * 70)          # nice visual break
    chunks: list[str] = ["\n".join(index_lines)]

    # ---- 2. file contents --------------------------------------------------
    for f in files:
        rel = f.relative_to(root)
        chunks.append(f"{HEADING_LINE}\n### {rel}\n{HEADING_LINE}")
        try:
            txt = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            txt = f.read_text(encoding="latin-1")
        chunks.append(txt.rstrip())
        chunks.append("")                 # blank line between files

    return "\n".join(chunks)


def human_size(n: int) -> str:
    for unit in ["B", "KiB", "MiB", "GiB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TiB"


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        sys.exit(f"❌ Root path does not exist: {root}")

    patterns = DEFAULT_EXCLUDE + args.exclude
    log = (lambda *_: None) if args.quiet else print

    if not args.quiet:
        print(f"Scanning inside: {root}")
        print("Exclude globs:")
        print(textwrap.indent('\n'.join(patterns), prefix="  · "))

    files = gather_files(root, patterns, log)
    if not files:
        sys.exit("🤔 No files matched — nothing to snapshot!")

    snapshot = build_snapshot(files, root)

    # 🔑 File name based on folder name
    folder_name = root.name
    out_name = args.output or f"{folder_name}_code.txt"

    # 🔑 Save in "code" subfolder
    snapshots_dir = root / "_code"
    snapshots_dir.mkdir(exist_ok=True)
    out_path = snapshots_dir / out_name
    out_path.write_text(snapshot, encoding="utf-8")

    total_bytes = sum(f.stat().st_size for f in files)
    if not args.quiet:
        print("\nSummary\n" + "-"*60)
    print(f"✔️ Snapshot saved to {out_path}")
    print(f"   Files stitched : {len(files)}")
    print(f"   Total size     : {human_size(total_bytes)}")




if __name__ == "__main__":
    main()
