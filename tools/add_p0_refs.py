#!/usr/bin/env python3
"""Add P0's references to index.html (Consolidated References, new first category)
and to tools/references.json (as _pending entries, ready to activate when files arrive).
Idempotent.  Usage: python tools/add_p0_refs.py [--no-push]
"""
import argparse
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = pathlib.Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
MANIFEST = TOOLS / "references.json"

CATEGORY_TITLE = "Set Theory, Order &amp; the Axiom of Choice"

ITEMS = [
    "Halmos, P.R. <em>Naive Set Theory</em>. Springer, 1974.",
    "Enderton, H.B. <em>Elements of Set Theory</em>. Academic Press, 1977.",
    "Jech, T. <em>The Axiom of Choice</em>. North-Holland, 1973; and <em>Set Theory</em>. Springer, 2003.",
    "Howard, P. &amp; Rubin, J. <em>Consequences of the Axiom of Choice</em>. AMS, 1998.",
    "Davey, B. &amp; Priestley, H. <em>Introduction to Lattices and Order</em>. Cambridge, 2002.",
]

PENDING = [
    {"file": "Halmos - Naive Set Theory.pdf",
     "keys": ["Halmos, P.R.", "Halmos"]},
    {"file": "Enderton - Elements of Set Theory.pdf",
     "keys": ["Enderton, H.B.", "Enderton"]},
    {"file": "Jech - The Axiom of Choice.pdf",
     "keys": ["Jech, T. <em>The Axiom of Choice</em>", "Jech"]},
    {"file": "Howard Rubin - Consequences of the Axiom of Choice.pdf",
     "keys": ["Consequences of the Axiom of Choice", "Howard–Rubin"]},
    {"file": "Davey Priestley - Introduction to Lattices and Order.pdf",
     "keys": ["Introduction to Lattices and Order", "Davey–Priestley"]},
]


def git(*args, check=True):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=check)


def patch_index(html: str) -> bool:
    if "Naive Set Theory" in html:
        print("index.html: P0 references already present — skipped")
        return False
    i = html.find('<div class="references-section"')
    if i == -1:
        print("warn: references-section not found; skipped index patch")
        return False
    h3 = html.find("<h3", i)
    if h3 == -1:
        print("warn: no category heading found in references section; skipped")
        return False
    # detect which list tag the categories use (ol or ul)
    ol, ul = html.find("<ol", i), html.find("<ul", i)
    tag = "ul" if (ul != -1 and (ol == -1 or ul < ol)) else "ol"
    items = "\n".join(f"      <li>{t}</li>" for t in ITEMS)
    block = (f'  <h3>{CATEGORY_TITLE}</h3>\n'
             f'  <{tag}>\n{items}\n  </{tag}>\n')
    html = html[:h3] + block + html[h3:]
    INDEX.write_text(html, encoding="utf-8")
    print(f"index.html: new reference category '{CATEGORY_TITLE}' inserted at the top")
    return True


def patch_manifest() -> bool:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    pend = data.setdefault("_pending", [])
    existing = {p.get("file") for p in pend} | {e.get("file") for e in data.get("entries", [])}
    added = [p for p in PENDING if p["file"] not in existing]
    if not added:
        print("references.json: P0 entries already present — skipped")
        return False
    pend.extend(added)
    MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"references.json: {len(added)} pending entr(ies) added for P0 references")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()

    changed = patch_index(INDEX.read_text(encoding="utf-8"))
    changed = patch_manifest() or changed
    if not changed:
        return

    git("add", "index.html", "tools/references.json")
    c = git("commit", "-m", "refs: add P0 references (set theory, order, AC) to syllabus + manifest",
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