#!/usr/bin/env python3
"""Inject a mobile-friendly CSS block into index.html (idempotent).
Fixes: topbar wrapping (brand + nav links), table horizontal scroll,
word-breaking of long math lines, paddings, quick-links and files-row on small screens.
Usage:  python tools/fix_mobile_css.py [--no-push]
"""
import argparse
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

CSS = """<style>/*mobilefix*/
@media(max-width:720px){
  #topbar{flex-wrap:wrap;gap:.35rem .8rem;padding:.5rem .9rem;}
  #topbar .brand{width:100%;text-align:center;}
  #topbar span:not(.brand){display:flex;flex-wrap:wrap;justify-content:center;gap:.3rem .95rem;width:100%;}
  #topbar a{margin-left:0;}
  .description{padding:1.2rem 1rem;}
  .quicklinks{gap:.4rem;}
  .quicklinks a{padding:.35rem .8rem;font-size:.8rem;}
  .toc-bar h2{font-size:1.3rem;}
  .session{padding:1rem .8rem;}
  .session ul li{overflow-wrap:break-word;}
  .session-refs{font-size:.8rem;}
  .session table{display:block;overflow-x:auto;}
  .files{margin-left:0;width:100%;justify-content:flex-start;}
}
</style>
"""


def git(*args, check=True):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=check)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()

    html = INDEX.read_text(encoding="utf-8")
    if "/*mobilefix*/" in html:
        print("index.html: mobile CSS already present — nothing to do")
        return
    html = html.replace("</head>", CSS + "</head>", 1)
    INDEX.write_text(html, encoding="utf-8")
    print("index.html: mobile-friendly CSS injected")

    git("add", "index.html")
    c = git("commit", "-m", "site: mobile-friendly topbar, tables, and spacing", check=False)
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