#!/usr/bin/env python3
"""Update the whole course site in one command.

Does three things (all idempotent — safe to re-run any time):
  1. Regenerates the sessions table in README.md      (between SESSIONS markers)
  2. Injects PDF/TeX chips next to each session title in index.html
  3. Writes materials.html (standalone materials list) from scratch

Usage:  python tools/update_site.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = pathlib.Path(__file__).resolve().parent
MANIFEST = TOOLS / "sessions.json"
README = ROOT / "README.md"
INDEX = ROOT / "index.html"
MATERIALS = ROOT / "materials.html"
LECTURES = ROOT / "lectures"
START = "<!-- SESSIONS:START -->"
END = "<!-- SESSIONS:END -->"
PAGES = "https://masoudmz.github.io/point-course"

CSS = """<style>/*files-links*/
.files{margin-left:auto;display:flex;gap:.4rem;align-items:center;}
.files a{font-size:.68rem;font-weight:700;text-decoration:none;border:1px solid var(--brass);color:var(--brass);border-radius:10px;padding:.08rem .55rem;}
.files a:hover{background:var(--brass);color:#fff;}
</style>
"""


def anchor(sid):
    """HTML anchor used in index.html: #sP1, #s23, ..."""
    return "#s" + (sid[1:] if sid.startswith("S") else sid)


def file_links(slug):
    out = ""
    if (LECTURES / f"{slug}.pdf").exists():
        out += f'<a href="lectures/{slug}.pdf">PDF</a>'
    if (LECTURES / f"{slug}.tex").exists():
        out += f'<a href="lectures/{slug}.tex">TeX</a>'
    return out


def update_readme(sessions):
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        print("warn: SESSIONS markers missing in README.md — skipped README update", file=sys.stderr)
        return 0
    rows, done, cur = [], 0, None
    for s in sessions:
        if s["act"] != cur:
            cur = s["act"]
            rows += ["", f"### {cur}", "",
                     "| ID | Session | Online | LaTeX | PDF | Status |",
                     "|:--:|---|---|:--:|:--:|:--:|"]
        slug, sid = s["slug"], s["id"]
        tex, pdf = LECTURES / f"{slug}.tex", LECTURES / f"{slug}.pdf"
        if pdf.exists():
            done += 1
            status = "✅ done"
        elif tex.exists():
            status = "🚧 notes only"
        else:
            status = "🚧 planned"
        rows.append(
            f"| {sid} | {s['title']} | [site]({PAGES}/{anchor(sid)}) | "
            + (f"[tex](lectures/{slug}.tex)" if tex.exists() else "—") + " | "
            + (f"[pdf](lectures/{slug}.pdf)" if pdf.exists() else "—") + f" | {status} |"
        )
    block = "\n".join(
        [START, "", f"> **Progress:** {done}/{len(sessions)} sessions have compiled lecture notes.", ""]
        + rows + ["", END]
    )
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    README.write_text(head + block + tail, encoding="utf-8")
    return done


def update_index(sessions):
    html = INDEX.read_text(encoding="utf-8")
    if "/*files-links*/" not in html:
        html = html.replace("</head>", CSS + "</head>", 1)
    if 'href="materials.html"' not in html:
        html = html.replace(
            '<a href="#refs">References</a>',
            '<a href="#refs">References</a><a href="materials.html">Materials</a>', 1)
    
    # remove any previously injected chips
    html = re.sub(r'\s*<span class="files">.*?</span>', '', html, flags=re.S)
    
    injected = 0
    for s in sessions:
        links = file_links(s["slug"])
        if not links:
            continue
        sid = anchor(s["id"]).lstrip("#")
        
        # find the session div
        pattern = r'(<div class="session" id="' + re.escape(sid) + r'">.*?<div class="session-title">.*?</div>)'
        m = re.search(pattern, html, re.S)
        if not m:
            print(f"warn: session {sid} pattern not found", file=sys.stderr)
            continue
        
        # insert chips after session-title div, before <ul>
        insert_pos = m.end()
        chip_html = f'\n    <span class="files">{links}</span>'
        html = html[:insert_pos] + chip_html + html[insert_pos:]
        injected += 1
    
    INDEX.write_text(html, encoding="utf-8")
    print(f"index.html: {injected} session chip(s) injected.")


def write_materials(sessions):
    rows, cur = [], None
    for s in sessions:
        if s["act"] != cur:
            cur = s["act"]
            rows.append(f"<h2>{cur}</h2><table><tr><th>ID</th><th>Session</th>"
                        "<th>LaTeX</th><th>PDF</th><th>In syllabus</th></tr>")
        slug = s["slug"]
        tex = f'<a href="lectures/{slug}.tex">tex</a>' if (LECTURES / f"{slug}.tex").exists() else "—"
        pdf = f'<a href="lectures/{slug}.pdf">pdf</a>' if (LECTURES / f"{slug}.pdf").exists() else "—"
        rows.append(f'<tr><td>{s["id"]}</td><td>{s["title"]}</td><td>{tex}</td><td>{pdf}</td>'
                    f'<td><a href="index.html{anchor(s["id"])}">syllabus §</a></td></tr>')
    body = "\n".join(rows)
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Point — Materials</title>
<style>
body{{font-family:Georgia,serif;background:#f5efe3;color:#241e16;margin:0;line-height:1.6;}}
header{{background:#14304a;color:#f4ecdc;padding:1.6rem;text-align:center;}}
header a{{color:#f3e6c8;}}
.wrap{{max-width:900px;margin:auto;padding:1.4rem;}}
table{{border-collapse:collapse;width:100%;margin:.6rem 0 1.6rem;background:#fffdf6;}}
th,td{{border:1px solid #e3dac8;padding:.4rem .6rem;text-align:left;font-size:.9rem;}}
th{{background:#14304a;color:#f4ecdc;}}
a{{color:#1e6e64;}}
</style></head><body>
<header><h1>Point — Course Materials</h1>
<p><a href="index.html">← back to syllabus</a> · <a href="dependencies.html">dependency diagram</a></p></header>
<div class="wrap">
<p>Every lecture file in the repository. Links appear only for files that exist;
this page is regenerated by <code>tools/update_site.py</code>.</p>
{body}
</div></body></html>
"""
    MATERIALS.write_text(html, encoding="utf-8")


def main():
    sessions = json.loads(MANIFEST.read_text(encoding="utf-8"))["sessions"]
    done = update_readme(sessions)
    update_index(sessions)
    write_materials(sessions)
    print(f"OK: README table ({done}/{len(sessions)} with PDFs), "
          f"index.html chips, materials.html written.")


if __name__ == "__main__":
    main()