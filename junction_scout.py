"""Win Junction Scout: Windows NTFS Junction Loop & Broken Reparse Point Auditor.

Scans directories for NTFS directory junctions, symbolic links, broken targets,
and dangerous recursive loops that cause search indexers, backup tools, and file
explorers to freeze or enter infinite recursion.
"""
import argparse
import json
import os
import sys


def get_link_target(path):
    """Retrieve link target using os.readlink or fallback."""
    try:
        return os.readlink(path)
    except (OSError, ValueError):
        try:
            real = os.path.realpath(path)
            if real != os.path.abspath(path):
                return real
        except Exception:
            pass
        return None


def scan_directory(root_path, max_depth=None):
    """Recursively scan root_path for junctions, symlinks, loops, and broken targets."""
    issues = []
    root_abs = os.path.abspath(root_path)
    if not os.path.exists(root_abs):
        return [{"type": "INVALID_PATH", "path": root_abs, "target": None}]

    visited_realpaths = set()
    root_depth = root_abs.count(os.sep)

    for base, dirs, files in os.walk(root_abs, topdown=True, followlinks=False):
        current_depth = os.path.abspath(base).count(os.sep) - root_depth
        if max_depth is not None and current_depth >= max_depth:
            dirs.clear()
            continue

        try:
            real_base = os.path.realpath(base)
        except Exception:
            real_base = base

        if real_base in visited_realpaths:
            issues.append({
                "type": "RECURSIVE_LOOP",
                "path": base,
                "target": real_base,
                "depth": current_depth,
            })
            dirs.clear()  # Do not traverse further into an infinite loop
            continue
        visited_realpaths.add(real_base)

        # Inspect subdirectories
        for d in list(dirs):
            full_path = os.path.join(base, d)
            try:
                is_link = os.path.islink(full_path)
            except OSError:
                is_link = False

            if is_link:
                target = get_link_target(full_path)
                target_exists = os.path.exists(target) if target else False
                if not target_exists:
                    issues.append({
                        "type": "BROKEN_JUNCTION",
                        "path": full_path,
                        "target": target,
                        "depth": current_depth + 1,
                    })
                else:
                    target_real = os.path.realpath(target)
                    if target_real in visited_realpaths or os.path.abspath(base).startswith(target_real):
                        issues.append({
                            "type": "RECURSIVE_LOOP",
                            "path": full_path,
                            "target": target,
                            "depth": current_depth + 1,
                        })
                    else:
                        issues.append({
                            "type": "VALID_JUNCTION",
                            "path": full_path,
                            "target": target,
                            "depth": current_depth + 1,
                        })

        # Inspect files for broken symlinks
        for f in files:
            full_path = os.path.join(base, f)
            try:
                if os.path.islink(full_path):
                    target = get_link_target(full_path)
                    if target and not os.path.exists(target):
                        issues.append({
                            "type": "BROKEN_SYMLINK",
                            "path": full_path,
                            "target": target,
                            "depth": current_depth + 1,
                        })
            except OSError:
                continue

    return issues


def format_summary(issues):
    counts = {}
    for item in issues:
        t = item.get("type", "UNKNOWN")
        counts[t] = counts.get(t, 0) + 1
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(description="Windows NTFS Junction Loop & Reparse Point Auditor")
    parser.add_argument("path", nargs="?", default=".", help="Root directory to inspect (default: .)")
    parser.add_argument("--max-depth", type=int, default=None, help="Maximum directory depth to traverse")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--summary", action="store_true", help="Display only statistical summary")
    parser.add_argument("--check", action="store_true", help="Exit code 1 if loops or broken links are detected")
    args = parser.parse_args(argv)

    issues = scan_directory(args.path, max_depth=args.max_depth)
    summary = format_summary(issues)

    if args.json:
        print(json.dumps({"summary": summary, "count": len(issues), "items": issues}, indent=2))
    elif args.summary:
        print(f"[*] Scan Summary for: {os.path.abspath(args.path)}")
        for k, v in summary.items():
            print(f"  {k:20s}: {v}")
    else:
        print(f"[*] Win Junction Scout - Auditing: {os.path.abspath(args.path)}\n")
        if not issues:
            print("[+] Clean: No junctions, broken links, or recursive loops found.")
        for item in issues:
            print(f"[{item['type']}] {item['path']}")
            if item.get("target"):
                print(f"    -> Target: {item['target']}")
        print(f"\n[*] Total detected items: {len(issues)}")
        for k, v in summary.items():
            print(f"    {k}: {v}")

    if args.check:
        has_problems = any(i["type"] in ("RECURSIVE_LOOP", "BROKEN_JUNCTION", "BROKEN_SYMLINK") for i in issues)
        if has_problems:
            sys.exit(1)


if __name__ == "__main__":
    main()
