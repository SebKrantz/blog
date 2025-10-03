#!/usr/bin/env python3
"""
Clean unused media files referenced by a single post (Markdown with embedded HTML or pure HTML).

Purpose
- Identify media files (images, video, audio, SVGs, etc.) under one or more project directories
  that are NOT referenced by a specific post, then optionally delete or back them up.

What the script does
1) Reads one post file (.md or .html).
2) Extracts local media references from:
   - HTML: src, href, poster attributes; <source src=...>; srcset; CSS url(...)
   - Markdown: images and links (![alt](path), [text](path))
   - HTML comments (<!-- ... -->) are ignored.
   - External refs (http/https) and data: URLs are ignored.
   - Query strings and fragments are stripped (e.g., image.jpg?v=2#x -> image.jpg).
3) Resolves relative paths with respect to the post file directory.
4) Scans the provided --roots directories for files with selected extensions.
5) Compares referenced vs. discovered files to find “unused” files.
6) Default is a dry run (no changes). With --delete, either delete unused files or move them to --backup-dir.

Key options
- --post PATH
  Path to the post file (.md or .html). All relative references are resolved against its directory.

- --format {auto|md|html} (default: auto)
  Parsing mode:
    md   -> Parse Markdown + embedded HTML (recommended for .md files that include HTML tags).
    html -> Parse HTML only.
    auto -> Guess based on the presence of HTML tags.

- --roots DIR [DIR ...]
  One or more directories to search and clean. Only files inside these roots are candidates for deletion/backup.

- --exts EXT [EXT ...]
  File extensions to consider as media. Include dots (e.g., .jpg .png .mp4).
  Default includes common image/video/audio types.

- --delete
  Perform changes. Without this flag, the script prints a dry-run preview only.

- --backup-dir PATH
  With --delete, move unused files into this directory instead of deleting them.
  Directory structure under each root is preserved.

- --keep-unused-list PATH
  Write the list of unused files to a text file (one path per line).

- --verbose
  Print per-file actions (moves/deletions) and extra info.

Matching details and safeguards
- Relative paths are normalized against the post’s directory and URL-encoded characters are decoded.
- Only files within --roots and matching --exts are considered for cleanup.
- Case-insensitive robustness: referenced paths are matched against discovered files case-insensitively.
  If no exact path match exists, a basename fallback match is attempted.
- HTML comments are removed before parsing, so commented-out assets do not count as used.
- http/https and data: URLs are always ignored.

Typical usage
- Dry run (Markdown with embedded HTML):
  python clean_unused_media.py --post content/posts/trip/index.md --format md --roots content/posts --dry-run

- Delete unused files (no backup):
  python clean_unused_media.py --post content/posts/trip/index.md --format md --roots content/posts --delete

- Move unused files to backup instead of deleting:
  python clean_unused_media.py --post content/posts/trip/index.md --format md --roots content/posts --backup-dir backup_unused --delete

Workflow recommendation
1) Commit your repo or make a backup.
2) Run a dry run and review output (optionally write the list with --keep-unused-list).
3) Run with --delete, and consider using --backup-dir for a reversible cleanup.

Exit codes
- 0 on success, non-zero on errors (e.g., post file missing).
"""

import argparse
import os
import re
import sys
import shutil
from urllib.parse import unquote, urlparse

# Patterns
HTML_ATTR_PATTERN = re.compile(r'\b(?:src|href|poster)\s*=\s*([\'"])(.*?)\1', re.IGNORECASE | re.DOTALL)
SOURCE_TAG_PATTERN = re.compile(r'<source\b[^>]*\bsrc\s*=\s*([\'"])(.*?)\1', re.IGNORECASE | re.DOTALL)
HTML_SRCSET_PATTERN = re.compile(r'\bsrcset\s*=\s*([\'"])(.*?)\1', re.IGNORECASE | re.DOTALL)
CSS_URL_PATTERN = re.compile(r'url\(\s*([\'"]?)([^\'")]+)\1\s*\)', re.IGNORECASE)
MD_LINK_PATTERN = re.compile(r'!\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)|\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
HTML_COMMENT_PATTERN = re.compile(r'<!--.*?-->', re.DOTALL)

def is_data_url(s: str) -> bool:
    return s.strip().lower().startswith("data:")

def is_http_url(s: str) -> bool:
    try:
        return urlparse(s).scheme in ("http", "https")
    except Exception:
        return False

def strip_query_fragment(path: str) -> str:
    path = path.split('#', 1)[0]
    path = path.split('?', 1)[0]
    return path

def normalize_path(ref: str, base_dir: str) -> str | None:
    if not ref:
        return None
    if is_http_url(ref) or is_data_url(ref):
        return None
    ref = unquote(ref.strip())
    ref = strip_query_fragment(ref)
    if not ref:
        return None
    if os.path.isabs(ref):
        return os.path.normpath(ref)
    return os.path.normpath(os.path.join(base_dir, ref))

def parse_srcset(value: str) -> list[str]:
    out = []
    for part in value.split(','):
        part = part.strip()
        if not part:
            continue
        url = part.split()[0]
        if url:
            out.append(url)
    return out

def remove_html_comments(text: str) -> str:
    return HTML_COMMENT_PATTERN.sub("", text)

def extract_paths_from_html(html: str) -> set[str]:
    paths = set()
    html_nc = remove_html_comments(html)
    for m in HTML_ATTR_PATTERN.finditer(html_nc):
        paths.add(m.group(2))
    for m in SOURCE_TAG_PATTERN.finditer(html_nc):
        paths.add(m.group(2))
    for m in HTML_SRCSET_PATTERN.finditer(html_nc):
        for url in parse_srcset(m.group(2)):
            paths.add(url)
    for m in CSS_URL_PATTERN.finditer(html_nc):
        paths.add(m.group(2))
    return paths

def extract_paths_from_markdown(md: str) -> set[str]:
    paths = set()
    md_nc = remove_html_comments(md)
    for m in MD_LINK_PATTERN.finditer(md_nc):
        for g in (1, 2):
            val = m.group(g)
            if val:
                paths.add(val)
    # Also parse any embedded HTML
    paths |= extract_paths_from_html(md_nc)
    return paths

def guess_is_html(text: str) -> bool:
    return bool(re.search(r'</?(html|body|img|a|video|source|picture|link|script|div)\b', text, re.IGNORECASE))

def gather_references(post_content: str, mode: str) -> set[str]:
    # mode: "md", "html", or "auto"
    if mode == "md":
        return extract_paths_from_markdown(post_content)
    if mode == "html":
        return extract_paths_from_html(post_content)
    # auto
    if guess_is_html(post_content):
        return extract_paths_from_html(post_content)
    return extract_paths_from_markdown(post_content)

def collect_files_in_roots(roots: list[str], exts: set[str]) -> set[str]:
    files = set()
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                if not exts or os.path.splitext(fn)[1].lower() in exts:
                    files.add(os.path.normpath(os.path.join(dirpath, fn)))
    return files

def main():
    parser = argparse.ArgumentParser(description="Remove or archive media files not referenced by a given post.")
    parser.add_argument("--post", required=True, help="Path to the blog post file (.md or .html).")
    parser.add_argument("--format", choices=["md", "html", "auto"], default="auto",
                        help="Parsing mode: md (Markdown+embedded HTML), html (HTML only), or auto (guess).")
    parser.add_argument("--roots", required=True, nargs="+", help="Directories under which media lives and should be cleaned.")
    parser.add_argument("--exts", nargs="*", default=[
        ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg",
        ".mp4", ".mov", ".webm", ".avi", ".mkv",
        ".mp3", ".wav", ".ogg", ".heic"
    ], help="Which file extensions are considered media (include dots).")
    parser.add_argument("--delete", action="store_true", help="Actually delete unused files. Default is dry run.")
    parser.add_argument("--backup-dir", default=None, help="If set with --delete, move unused files here instead of deleting.")
    parser.add_argument("--keep-unused-list", default=None, help="Write list of unused files to this path.")
    parser.add_argument("--verbose", action="store_true", help="Verbose output.")
    args = parser.parse_args()

    post_path = os.path.abspath(args.post)
    if not os.path.isfile(post_path):
        print(f"Error: Post not found: {post_path}", file=sys.stderr)
        sys.exit(1)

    with open(post_path, "r", encoding="utf-8") as f:
        content = f.read()

    base_dir = os.path.dirname(post_path)
    roots_abs = [os.path.abspath(r) for r in args.roots]
    exts = {e.lower() if e.startswith(".") else "." + e.lower() for e in args.exts}

    # Extract references
    raw_refs = gather_references(content, args.format)
    # Normalize to absolute paths
    normalized = set()
    for ref in raw_refs:
        norm = normalize_path(ref, base_dir)
        if norm:
            normalized.add(norm)

    # Keep only references under roots and with matching extension
    def in_roots(path: str) -> bool:
        p = os.path.abspath(path)
        return any(os.path.exists(r) and os.path.commonpath([p, r]) == r for r in roots_abs)

    referenced_abs = {p for p in normalized if in_roots(p) and os.path.splitext(p)[1].lower() in exts}

    # Collect all media files in roots
    all_media = collect_files_in_roots(roots_abs, exts)

    # Case-insensitive robustness
    media_lower_map = {}
    for p in all_media:
        media_lower_map.setdefault(p.lower(), set()).add(p)

    protected = set()
    for p in referenced_abs:
        low = p.lower()
        if low in media_lower_map:
            protected |= media_lower_map[low]
        else:
            # Fallback to basename match
            base = os.path.basename(low)
            for k, vals in media_lower_map.items():
                if os.path.basename(k) == base:
                    protected |= vals

    unused = sorted(p for p in all_media if p not in protected)

    # Optional list output
    if args.keep_unused_list:
        out_path = os.path.abspath(args.keep_unused_list)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            for p in unused:
                f.write(p + "\n")

    print(f"Post: {post_path}")
    print(f"Format: {args.format}")
    print(f"Roots: {', '.join(roots_abs)}")
    print(f"Total media files discovered: {len(all_media)}")
    print(f"Referenced (protected) files: {len(protected)}")
    print(f"Unused candidate files: {len(unused)}")

    if not args.delete:
        print("\nDry run. Unused files:")
        for p in unused:
            print(p)
        print("\nRe-run with --delete to remove, or add --backup-dir to move unused files into a backup.")
        return

    # Deletion or backup
    if args.backup_dir:
        backup_root = os.path.abspath(args.backup_dir)
        os.makedirs(backup_root, exist_ok=True)
        moved = 0
        for p in unused:
            rel = None
            ap = os.path.abspath(p)
            for r in roots_abs:
                if os.path.commonpath([ap, r]) == r:
                    rel = os.path.relpath(ap, r)
                    break
            dest = os.path.join(backup_root, rel if rel else os.path.basename(p))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            if args.verbose:
                print(f"Moving {p} -> {dest}")
            try:
                shutil.move(p, dest)
                moved += 1
            except Exception as e:
                print(f"Failed to move {p}: {e}", file=sys.stderr)
        print(f"Moved {moved} files to backup: {backup_root}")
    else:
        removed = 0
        for p in unused:
            if args.verbose:
                print(f"Deleting {p}")
            try:
                os.remove(p)
                removed += 1
            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"Failed to delete {p}: {e}", file=sys.stderr)
        print(f"Deleted {removed} files.")

if __name__ == "__main__":
    main()