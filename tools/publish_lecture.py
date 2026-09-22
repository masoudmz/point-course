#!/usr/bin/env python3
"""One-command publish pipeline for a lecture.

Usage:
    python tools/publish_lecture.py S2                 # by session id
    python tools/publish_lecture.py S2-modules         # by slug
    python tools/publish_lecture.py lectures/S2-modules.tex
    python tools/publish_lecture.py S2 --no-push       # everything except push

Steps performed:
  [1/4] compile lectures/<slug>.tex  ->  lectures/<slug>.pdf   (latexmk, else pdflatex x2)
  [2/4] refresh the site (README table, index chips, materials.html) via update_site.py
  [3/4] git add + commit (tex, pdf, and refreshed site files)
  [4/4] git push (unless --no-push)
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = pathlib.Path(__file__).resolve().parent
LECTURES = ROOT / "lectures"


def load_sessions():
    return json.loads((TOOLS / "sessions.json").read_text(encoding="utf-8"))["sessions"]


def resolve(target: str):
    """Return (sid, slug, title) for an id, slug, or path."""
    t = target.replace("\\", "/").rstrip("/")
    stem = pathlib.PurePosixPath(t).stem  # works for 'lectures/S2-modules.tex' too
    for s in load_sessions():
        if t == s["id"] or t.lower() == s["id"].lower():
            return s["id"], s["slug"], s["title"]
        if t == s["slug"] or stem == s["slug"]:
            return s["id"], s["slug"], s["title"]
    ids = ", ".join(s["id"] for s in load_sessions())
    sys.exit(f"error: '{target}' matches no session. Valid ids: {ids}")


def compile_tex(tex: pathlib.Path) -> pathlib.Path:
    pdf = tex.with_suffix(".pdf")
    ok = False
    if shutil.which("latexmk") and shutil.which("perl"):
        try:
            subprocess.run(
                ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", str(tex)],
                cwd=tex.parent, check=True)
            ok = pdf.exists()
        except subprocess.CalledProcessError:
            ok = False
    if not ok:
        print("      (latexmk unavailable/failed -> pdflatex x2)")
        for i in (1, 2):
            r = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name],
                cwd=tex.parent)
            if r.returncode != 0:
                sys.exit(f"error: pdflatex failed (pass {i}); check {tex.with_suffix('.log')}")
    if not pdf.exists():
        sys.exit(f"error: {pdf} was not produced")
    return pdf


def git(*args: str, check: bool = True):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=check)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="session id (S2), slug (S2-modules), or path to the .tex")
    ap.add_argument("--no-push", action="store_true", help="skip the final git push")
    args = ap.parse_args()

    sid, slug, title = resolve(args.target)
    tex = LECTURES / f"{slug}.tex"
    if not tex.exists():
        sys.exit(f"error: {tex} not found. Put the lecture .tex there first.")

    print(f"[1/4] compiling {tex.relative_to(ROOT)} ...")
    pdf = compile_tex(tex)
    print(f"      -> {pdf.relative_to(ROOT)}")

    print("[2/4] refreshing site (README, index chips, materials.html) ...")
    subprocess.run([sys.executable, str(TOOLS / "update_site.py")], cwd=ROOT, check=True)

    print("[3/4] committing ...")
    git("add", str(tex.relative_to(ROOT)), str(pdf.relative_to(ROOT)),
        "index.html", "materials.html", "README.md")
    msg = f"lectures: publish {sid} ({title}); refresh site"
    c = git("commit", "-m", msg, check=False)
    if c.returncode != 0:
        print("      (nothing new to commit)")

    if args.no_push:
        print("[4/4] push skipped (--no-push)")
    else:
        print("[4/4] pushing ...")
        p = git("push", check=False)
        if p.returncode != 0:
            print("warn: push failed (offline?). Commit is local; push later with: git push")

    print(f"done: {sid} published.")


if __name__ == "__main__":
    main()