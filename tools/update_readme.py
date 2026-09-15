#!/usr/bin/env python3
"""Regenerate the sessions table in README.md from tools/sessions.json + files on disk.

Usage:  python tools/update_readme.py
It rewrites everything between the markers
    <!-- SESSIONS:START -->  ...  <!-- SESSIONS:END -->
leaving the rest of README.md untouched.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = pathlib.Path(__file__).resolve().parent / "sessions.json"
README = ROOT / "README.md"
START = "<!-- SESSIONS:START -->"
END = "<!-- SESSIONS:END -->"
PAGES = "https://USERNAME.github.io/point-course"   # TODO: your GitHub username


def anchor(sid: str) -> str:
    """HTML anchor used in index.html: #sP1, #s23, ..."""
    return "#s" + (sid[1:] if sid.startswith("S") else sid)


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        print("error: SESSIONS markers not found in README.md", file=sys.stderr)
        return 1

    lectures = ROOT / "lectures"
    rows, done, cur = [], 0, None

    for s in data["sessions"]:
        if s["act"] != cur:
            cur = s["act"]
            rows += [
                "",
                f"### {cur}",
                "",
                "| ID | Session | Online | LaTeX | PDF | Status |",
                "|:--:|---|---|:--:|:--:|:--:|",
            ]
        slug, sid = s["slug"], s["id"]
        tex = lectures / f"{slug}.tex"
        pdf = lectures / f"{slug}.pdf"
        if pdf.exists():
            done += 1
            status = "✅ done"
        elif tex.exists():
            status = "🚧 notes only"
        else:
            status = "🚧 planned"
        online = f"[site]({PAGES}/{anchor(sid)})"
        texl = f"[tex](lectures/{slug}.tex)" if tex.exists() else "—"
        pdfl = f"[pdf](lectures/{slug}.pdf)" if pdf.exists() else "—"
        rows.append(f"| {sid} | {s['title']} | {online} | {texl} | {pdfl} | {status} |")

    total = len(data["sessions"])
    block = "\n".join(
        [START, "", f"> **Progress:** {done}/{total} sessions have compiled lecture notes.", ""]
        + rows
        + ["", END]
    )
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    README.write_text(head + block + tail, encoding="utf-8")
    print(f"README.md updated: {done}/{total} sessions with compiled PDFs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())