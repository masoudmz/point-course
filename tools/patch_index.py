#!/usr/bin/env python3
"""One-off patch for index.html (robust version):
  1) clean versioned/edition wording from <title> and the top-bar brand
  2) add a Dependencies link to the top bar
  3) add a prominent quick-links bar (Materials / Dependencies / References) just above the TOC
Idempotent: safe to re-run.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

CSS = """<style>/*quicklinks*/
.quicklinks{display:flex;gap:.6rem;flex-wrap:wrap;justify-content:center;margin:0 0 1.6rem;}
.quicklinks a{font-size:.85rem;font-weight:700;text-decoration:none;border:1.5px solid var(--brass);color:var(--brass);border-radius:999px;padding:.4rem 1rem;background:var(--card);}
.quicklinks a:hover{background:var(--brass);color:#fff;}
</style>
"""

NAV = """<nav class="quicklinks">
  <a href="materials.html">Materials (TeX / PDF)</a>
  <a href="dependencies.html">Dependency diagram</a>
  <a href="#refs">References</a>
</nav>
"""

CLEAN_TITLE = "<title>Point — From Number Theory to Algebraic Geometry and Logic</title>"
CLEAN_BRAND = '<span class="brand">POINT · A Year-Long Course</span>'

TOC_MARKERS = ('id="toc"', 'class="toc"', 'class="toc-bar"',
               'class="timeline"', 'class="toc-grid"', 'class="toc-act"')


def find_toc_start(html: str) -> int:
    """Start of the TOC block, tolerant to attribute order / extra classes / line breaks."""
    for marker in TOC_MARKERS:
        pos = html.find(marker)
        if pos != -1:
            return html.rfind('<', 0, pos)   # start of the tag containing the marker
    pos = html.find('Contents')
    if pos != -1:
        return html.rfind('<div', 0, pos)
    return -1


def main():
    html = INDEX.read_text(encoding="utf-8")
    changed = []

    # 1) clean title / brand / edition wording
    m = re.search(r"<title>.*?</title>", html, re.S)
    if m and m.group(0) != CLEAN_TITLE:
        html = html[:m.start()] + CLEAN_TITLE + html[m.end():]
        changed.append("title cleaned")
    b = re.search(r'<span class="brand">.*?</span>', html, re.S)
    if b and b.group(0) != CLEAN_BRAND:
        html = html[:b.start()] + CLEAN_BRAND + html[b.end():]
        changed.append("top-bar brand cleaned")
    for junk in ("Merged Maximal Edition", "Maximal Edition", "Merged version",
                 "merged maximal", " · v2.1", " (v2.1)", " · v2.0", " (v2.0)"):
        if junk in html:
            html = html.replace(junk, "")
            changed.append(f"removed '{junk.strip()}'")

    toc_start = find_toc_start(html)
    if toc_start == -1:
        sys.exit("error: cannot locate the TOC block at all.\n"
                 "Send the output of:  Select-String -Path index.html -Pattern 'toc' | Select-Object -First 6")

    head_part, tail_part = html[:toc_start], html[toc_start:]

    # 2) top-bar Dependencies link (only look above the TOC)
    if 'href="dependencies.html"' not in head_part:
        if '<a href="materials.html">Materials</a>' in head_part:
            head_part = head_part.replace(
                '<a href="materials.html">Materials</a>',
                '<a href="materials.html">Materials</a><a href="dependencies.html">Dependencies</a>', 1)
            changed.append("top-bar Dependencies link added")
        elif '<a href="#refs">References</a>' in head_part:
            head_part = head_part.replace(
                '<a href="#refs">References</a>',
                '<a href="#refs">References</a><a href="dependencies.html">Dependencies</a>', 1)
            changed.append("top-bar Dependencies link added")
        else:
            print("warn: top-bar anchors not found; skipped top-bar link", file=sys.stderr)
    html = head_part + tail_part

    # 3) quick-links bar + CSS (once)
    if "/*quicklinks*/" not in html:
        html = html.replace("</head>", CSS + "</head>", 1)
        changed.append("quick-links CSS added")
    if '<nav class="quicklinks">' not in html:
        toc_start = find_toc_start(html)   # recompute after head edits
        html = html[:toc_start] + NAV + html[toc_start:]
        changed.append("quick-links bar inserted")

    INDEX.write_text(html, encoding="utf-8")
    print("index.html patched:", "; ".join(changed) if changed else "nothing to do")


if __name__ == "__main__":
    main()