#!/usr/bin/env python3
"""Restyle/move the detailed-syllabus pointer in index.html:
   - remove the cream box (the <p class="syllabus-pointer"> paragraph AND its CSS block)
   - append the reworded sentence inline at the END of the paragraph that precedes
     the 'Anatomy of ...' paragraph (link on the word "this")
Idempotent: safe to re-run.
Usage:  python tools/fix_syllabus_pointer.py [--no-push]
"""
import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

SENTENCE = (' <strong>Detailed syllabus (printable PDF):</strong> for a fuller '
            'session-by-session description — goals, complete proof lists, course-role '
            'and references — read <a href="syllabus/syllabus.pdf">this</a>.')

GUARD = 'read <a href="syllabus/syllabus.pdf">this</a>'


def git(*args, check=True):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=check)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()

    html = INDEX.read_text(encoding="utf-8")
    if GUARD in html:
        print("index.html: new pointer already in place — nothing to do")
        return

    # 1) remove the old boxed paragraph (includes the Persian line inside it)
    html, n1 = re.subn(r'\s*<p class="syllabus-pointer">.*?</p>', '', html, flags=re.S)
    # 2) remove its CSS block (the cream box styles)
    html, n2 = re.subn(r'<style>/\*syllabuslink\*/.*?</style>\s*', '', html, flags=re.S)

    # 3) append the sentence to the paragraph that precedes 'Anatomy of ...'
    m = re.search(r'Anatomy of', html)
    if m:
        p_start = html.rfind('<p', 0, m.start())          # opening of the Anatomy paragraph
        prev_close = html.rfind('</p>', 0, p_start)      # closing of the paragraph before it
        if prev_close == -1:
            sys.exit("error: cannot locate the paragraph before 'Anatomy of'")
        html = html[:prev_close] + SENTENCE + html[prev_close:]
        where = "appended to the paragraph before 'Anatomy of...'"
    else:
        # fallback: last paragraph of the description block
        md = re.search(r'<div class="description">.*?</div>', html, flags=re.S)
        if not md:
            sys.exit("error: description block not found")
        block = md.group(0)
        last = block.rfind('</p>')
        html = html[:md.start()] + block[:last] + SENTENCE + block[last:] + html[md.end():]
        where = "appended to the last description paragraph (fallback)"

    INDEX.write_text(html, encoding="utf-8")
    print(f"index.html: cream box removed ({n1} paragraph, {n2} css block); sentence {where}")

    git("add", "index.html")
    c = git("commit", "-m", "site: inline the detailed-syllabus pointer before the Anatomy note",
            check=False)
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