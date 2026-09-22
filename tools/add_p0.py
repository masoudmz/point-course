#!/usr/bin/env python3
"""Insert session P0 (Set Theory, Order, AC) at the very beginning of the course:
   - index.html: TOC chip, session block before P1, meeting counts 64 -> 65
   - tools/sessions.json: P0 entry at the head of the sessions list
   - dependencies.html: P0 node + edges START->P0, P0->S1, P0->S3, P0->S58
Idempotent.  Usage: python tools/add_p0.py [--no-push]
"""
import argparse
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = pathlib.Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
SESSIONS = TOOLS / "sessions.json"
DEPS = ROOT / "dependencies.html"

CHIP = '<a class="chip" href="#sP0"><span class="n">P0</span> Set Theory, Order &amp; Choice</a>'

SESSION_BLOCK = '''  <div class="session" id="sP0"><div class="session-title"><span class="session-number">P0</span><h3>Set Theory, Order, and the Axiom of Choice</h3></div>
    <ul>
      <li>Equivalence relations and their canonical bijection with partitions; quotient sets</li>
      <li>Preorders, partial orders, strict orders and their correspondences; a preorder becomes a poset on its quotient</li>
      <li>Minimum vs minimal, maximum vs maximal, upper/lower bounds, suprema; well-orders and decreasing chains</li>
      <li>From Russell's paradox to ZF: the axioms and what each one buys</li>
      <li>Axiom of Choice; equivalents: Well-Ordering and Zorn (WO⇒AC and Zorn⇒AC proved; AC⇒WO, AC⇒Zorn sketched)</li>
      <li>Famous equivalents: basis of every vector space, Tychonoff, Tarski's |A×A|=|A|, spanning trees; the Completeness Theorem's true tier (BPI)</li>
      <li>Where the course spends Zorn: S1 (Krull), S3 (algebraic closure), S58 (Deligne)</li>
    </ul>
    <div class="session-refs"><strong>Refs:</strong> Halmos; Enderton; Jech; Howard–Rubin; Davey–Priestley.</div>
    <span class="backtop"><a href="#toc">↑ contents</a></span></div>
'''


def git(*args, check=True):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=check)


def patch_index(html: str) -> str:
    if 'href="#sP0"' not in html:
        html = html.replace('<a class="chip" href="#sP1">', CHIP + '<a class="chip" href="#sP1">', 1)
    if 'id="sP0"' not in html:
        html = html.replace('<div class="session" id="sP1">', SESSION_BLOCK + '<div class="session" id="sP1">', 1)
    html = html.replace("64 Meetings (P1–P3 + S1–S61)", "65 Meetings (P0–P3 + S1–S61)")
    html = html.replace("64 meetings (P1–P3 + S1–S61)", "65 meetings (P0–P3 + S1–S61)")
    return html


def patch_sessions_json() -> None:
    data = json.loads(SESSIONS.read_text(encoding="utf-8"))
    if any(s["id"] == "P0" for s in data["sessions"]):
        return
    data["sessions"].insert(0, {
        "act": "Prelude — Essential Prerequisites",
        "id": "P0",
        "title": "Set Theory, Order, and the Axiom of Choice",
        "slug": "P0-sets"
    })
    SESSIONS.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def patch_deps(html: str) -> str:
    if '"P0"' in html:
        return html
    html = html.replace('["P1","Group Theory I",0],',
                        '["P0","Set Theory & Choice",0],["P1","Group Theory I",0],', 1)
    html = html.replace('["START","P1"],',
                        '["START","P0"],["P0","S1"],["P0","S3"],["P0","S58"],["START","P1"],', 1)
    return html


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()

    INDEX.write_text(patch_index(INDEX.read_text(encoding="utf-8")), encoding="utf-8")
    print("index.html: P0 chip, session block, and counts updated")
    patch_sessions_json()
    print("sessions.json: P0 inserted at head")
    if DEPS.exists():
        DEPS.write_text(patch_deps(DEPS.read_text(encoding="utf-8")), encoding="utf-8")
        print("dependencies.html: P0 node and edges added")
    else:
        print("note: dependencies.html not found; skipped")

    git("add", "index.html", "tools/sessions.json")
    if DEPS.exists():
        git("add", "dependencies.html")
    c = git("commit", "-m", "site: add session P0 (Set Theory, Order, AC) at the head of the course",
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