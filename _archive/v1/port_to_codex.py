#!/usr/bin/env python3
"""Codex port helper for aidlc-devflow style repositories.

What this script does:
1) Rewrites `_shared/...` references in `skills/*/SKILL.md` to `../_shared/...`
2) Rewrites `skills/_shared/...` references in `skills/*/SKILL.md` to `../_shared/...`
3) Rewrites Claude slash-invocations (`/aidlc:skill-name`) to Codex style (`$skill-name`)

Run with `--apply` to write changes. Without it, the script performs a dry run.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileChange:
    path: Path
    replacements: int


def replace_shared_refs(text: str) -> tuple[str, int]:
    count = 0

    # 1) Explicit root-based shared references inside skills
    text, n = re.subn(r"\bskills/_shared/", "../_shared/", text)
    count += n

    # 2) Bare _shared path tokens (not already relative or absolute)
    text, n = re.subn(r"(?<![A-Za-z0-9_./-])_shared/", "../_shared/", text)
    count += n

    return text, count


def replace_invocations(text: str) -> tuple[str, int]:
    # /aidlc:aidlc-using-devflow -> $aidlc-using-devflow
    return re.subn(r"/aidlc:([a-z0-9][a-z0-9-]*)", r"$\1", text)


def process_file(path: Path, *, rewrite_shared: bool, rewrite_invocations: bool) -> tuple[str, int]:
    original = path.read_text(encoding="utf-8")
    updated = original
    total = 0

    if rewrite_shared:
        updated, n = replace_shared_refs(updated)
        total += n

    if rewrite_invocations:
        updated, n = replace_invocations(updated)
        total += n

    return updated, total


def collect_targets(root: Path, rewrite_shared: bool, rewrite_invocations: bool) -> list[Path]:
    targets: list[Path] = []

    if rewrite_shared:
        targets.extend(sorted((root / "skills").glob("*/SKILL.md")))

    if rewrite_invocations:
        for pattern in ["README.md", "README.en.md", "hooks/session-start"]:
            p = root / pattern
            if p.exists():
                targets.append(p)
        # Keep rewrite scope to user-facing docs to avoid mutating historical plans/analysis.
        guide_dir = root / "docs" / "guide"
        if guide_dir.exists():
            targets.extend(sorted(guide_dir.rglob("*.md")))
        for pattern in ["docs/testing.md", "docs/claude-md-devflow-only.md"]:
            p = root / pattern
            if p.exists():
                targets.append(p)

    # Deduplicate while preserving order
    seen: set[Path] = set()
    deduped: list[Path] = []
    for p in targets:
        if p in seen:
            continue
        seen.add(p)
        deduped.append(p)

    return deduped


def main() -> int:
    parser = argparse.ArgumentParser(description="Port helper: Claude-style skill repo -> Codex-friendly layout")
    parser.add_argument("--root", default=".", help="Repository root path (default: current directory)")
    parser.add_argument("--apply", action="store_true", help="Write changes to files (default: dry run)")
    parser.add_argument(
        "--rewrite-shared",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Rewrite _shared references in SKILL.md files",
    )
    parser.add_argument(
        "--rewrite-invocations",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Rewrite /aidlc:... invocations to $skill-name",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"ERROR: root path not found: {root}", file=sys.stderr)
        return 2

    targets = collect_targets(root, args.rewrite_shared, args.rewrite_invocations)
    file_changes: list[FileChange] = []

    for path in targets:
        if not path.exists() or not path.is_file():
            continue

        updated, count = process_file(
            path,
            rewrite_shared=args.rewrite_shared,
            rewrite_invocations=args.rewrite_invocations,
        )
        if count == 0:
            continue

        if args.apply:
            path.write_text(updated, encoding="utf-8")

        file_changes.append(FileChange(path=path, replacements=count))

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[{mode}] root={root}")
    if not file_changes:
        print("No changes needed.")
        return 0

    total_replacements = sum(c.replacements for c in file_changes)
    print(f"Files changed: {len(file_changes)}")
    print(f"Total replacements: {total_replacements}")
    print("---")
    for change in file_changes:
        rel = change.path.relative_to(root)
        print(f"{rel}: {change.replacements}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
