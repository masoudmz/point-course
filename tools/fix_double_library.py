#!/usr/bin/env python3
"""Keep exactly ONE 'Library' link (topbar) and ONE 'Reference files' link (quicklinks),
pointing at the live references folder; remove duplicates from old folder spellings.
Idempotent.  Usage: python tools/fix_double_library.py [--no-push]
"""
import argparse
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

ANY_LIB = re.compile(
    r'<a href="(?:references|refrends)/index\.html">(?:Library|Reference files)</a>')


def git(*args, check=True):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=check)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()

    folder = "references" if (ROOT / "references").is_dir() else "refrends"
    html = INDEX.read_text(encoding="utf-8")
    removed = len(ANY_LIB.findall(html))
    html = ANY_LIB.sub('', html)

    # exactly one topbar link
    link = f'<a href="{folder}/index.html">Library</a>'
    for anchor in ['<a href="dependencies.html">Dependencies</a>',
                   '<a href="materials.html">Materials</a>',
                   '<a href="#refs">References</a>']:
        if anchor in html:
            html = html.replace(anchor, anchor + link, 1)
            break

    # exactly one quicklinks entry
    if '<nav class="quicklinks">' in html:
        html = html.replace('</nav>',
                            f'  <a href="{folder}/index.html">Reference files</a>\n</nav>', 1)

    INDEX.write_text(html, encoding="utf-8")
    print(f"removed {removed} stale/duplicate link(s); re-added exactly one per slot ({folder}/)")

    git("add", "index.html")
    c = git("commit", "-m", "site: dedupe Library link in topbar/quicklinks", check=False)
    if c.returncode != 0:
        print("      (nothing new to commit)")
    if args.no_push:
        print("push skipped (--no-push)")
    else:
        p = git("push", check=False)
        if p.returncode != 0:
            print("warn: push failed (offline?). Commit is local; push later with: git push")
    print("done.")


if __name__ == "__main__":
    main()