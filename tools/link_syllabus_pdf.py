#!/usr/bin/env python3
"""Add a pointer line in the Course Description of index.html linking to the
detailed syllabus PDF (syllabus/syllabus.pdf) and its LaTeX source.
Idempotent: safe to re-run; does nothing if the link already exists.

Usage:  python tools/link_syllabus_pdf.py [--no-push]
"""
import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
PDF = ROOT / "syllabus" / "syllabus.pdf"
TEX = ROOT / "syllabus" / "syllabus.tex"

CSS = """<style>/*syllabuslink*/
.syllabus-pointer{background:var(--brass-soft);border-left:4px solid var(--brass);
padding:.55rem .95rem;border-radius:0 6px 6px 0;font-size:.92rem;margin:.6rem 0;}
.syllabus-pointer a{color:#6b4a12;font-weight:700;text-decoration:none;border-bottom:1px dotted #6b4a12;}
.syllabus-pointer a:hover{background:var(--brass);color:#fff;}
</style>
"""

PARA = (
    '<p class="syllabus-pointer"><strong>Detailed syllabus (printable PDF):</strong> '
    'for a fuller session-by-session description — goals, complete proof lists, course-role '
    'and references — read <a href="syllabus/syllabus.pdf">syllabus/syllabus.pdf</a> '
    '(LaTeX source: <a href="syllabus/syllabus.tex">syllabus.tex</a>).<br>'
    '<span dir="rtl" style="font-size:.88rem;">شرح مفصل‌تر هر جلسه (اهداف، فهرست کامل اثبات‌ها، '
    'نقش جلسه در دوره و منابع) را در <a href="syllabus/syllabus.pdf">syllabus.pdf</a> بخوانید.</span></p>'
)


def git(*args, check=True):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=check)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()

    if not PDF.exists():
        print(f"warn: {PDF.relative_to(ROOT)} not found — the link will 404 until you add it",
              file=sys.stderr)

    html = INDEX.read_text(encoding="utf-8")
    if 'href="syllabus/syllabus.pdf"' in html:
        print("index.html: syllabus PDF link already present — nothing to do")
        return

    if "/*syllabuslink*/" not in html:
        html = html.replace("</head>", CSS + "</head>", 1)

    marker = '<div class="description">'
    i = html.find(marker)
    if i == -1:
        sys.exit("error: cannot locate the Course Description block in index.html")
    j = html.find("</p>", i)
    if j == -1:
        sys.exit("error: cannot locate the first paragraph of the description block")
    pos = j + len("</p>")
    html = html[:pos] + "\n  " + PARA + html[pos:]

    INDEX.write_text(html, encoding="utf-8")
    print("index.html: syllabus PDF pointer added to Course Description")

    git("add", "index.html")
    c = git("commit", "-m", "site: link detailed syllabus PDF from Course Description", check=False)
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