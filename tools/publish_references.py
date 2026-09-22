#!/usr/bin/env python3
"""Publish references (v4, self-healing):
  - auto-promotes _pending entries whose file now exists (dropping the file is enough)
  - REBUILDS every reference link & 'file' chip in index.html from scratch each run
    (consolidated <li> items + session Refs lines), removing stale/nested/duplicate markup
  - regenerates the Library listing; commits and pushes
Usage:  python tools/publish_references.py [--no-push]
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = pathlib.Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
FOLDER_CANDIDATES = ["references", "refrences"]
MANIFEST_CANDIDATES = [TOOLS / "references.json", TOOLS / "refrences.json",
                       ROOT / "references.json", ROOT / "refrences.json"]
TOPBAR_LABEL = "Library"
QUICK_LABEL = "Reference files"

CSS = """<style>/*reffiles*/
.filetag{font-size:.68rem;font-weight:700;text-decoration:none;border:1px solid var(--teal);color:var(--teal);border-radius:10px;padding:.05rem .5rem;margin-left:.35rem;white-space:nowrap;}
.session-refs a{color:var(--teal);text-decoration:none;border-bottom:1px dotted var(--teal);}
.session-refs a:hover{color:#fff;background:var(--teal);}
</style>
"""


def git(*args, check=True):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=check)


def pick_folder() -> pathlib.Path:
    for name in FOLDER_CANDIDATES:
        d = ROOT / name
        if d.is_dir():
            return d
    d = ROOT / "references"
    d.mkdir(parents=True, exist_ok=True)
    (d / ".gitkeep").write_text("", encoding="utf-8")
    return d


def norm(s: str) -> str:
    return re.sub(r"[\s\-_]+", "", unicodedata.normalize("NFC", s).lower())


def resolve_file(folder: pathlib.Path, name: str):
    cand = folder / name
    if cand.is_file():
        return cand.name
    stem = cand.stem
    for p in folder.iterdir():
        if p.is_file() and p.stem == stem:
            return p.name
    for p in folder.iterdir():
        if p.is_file() and norm(p.name) == norm(name):
            return p.name
    for p in folder.iterdir():
        if p.is_file() and norm(p.stem) == norm(stem):
            return p.name
    return None


def load_manifest():
    man = next((p for p in MANIFEST_CANDIDATES if p.exists()), None)
    if man is None:
        man = TOOLS / "references.json"
        man.write_text(json.dumps({"entries": [], "_pending": []}, indent=2), encoding="utf-8")
        return [], [], man
    data = json.loads(man.read_text(encoding="utf-8"))
    return data.get("entries", []), data.get("_pending", []), man


def promote(entries, pending, folder, man):
    """Move pending entries whose file now exists into entries (and fix file name)."""
    moved, rest = [], []
    for p in pending:
        f = resolve_file(folder, p["file"])
        if f:
            entries.append({**p, "file": f})
            moved.append(f)
        else:
            rest.append(p)
    if moved:
        data = json.loads(man.read_text(encoding="utf-8"))
        data["entries"] = entries
        data["_pending"] = rest
        man.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return moved


def unwrap(s: str) -> str:
    """Remove OUR anchors and file chips, keep the plain citation text (and <em> etc.)."""
    s = re.sub(r'<span class="filetag">.*?</span>', '', s, flags=re.S)
    for _ in range(10):
        if '<a' not in s:
            break
        s2 = re.sub(r'<a\b[^>]*>(.*?)</a>', r'\1', s, flags=re.S)
        if s2 == s:
            break
        s = s2
    s = s.replace('</a>', '')
    return re.sub(r'\s+', ' ', s).strip()


def rebuild(html: str, linked):
    """linked = list of (url, keys_sorted_longest_first) for entries with existing files."""
    head, sep, tail = html.partition('<div class="references-section"')
    if not sep:
        return html, 0

    # ── consolidated <li> items: rebuild from scratch ──
    n = 0
    def fix_li(m):
        nonlocal n
        plain = unwrap(m.group(1))
        for url, keys in linked:
            if any(k in plain for k in keys):
                n += 1
                return f'<li><a href="{url}">{plain}</a> <span class="filetag">file</span></li>'
        return f'<li>{plain}</li>'
    tail = re.sub(r'<li>(.*?)</li>', fix_li, tail, flags=re.S)

    # ── session Refs lines: strip old links, re-link keys in plain text only ──
    def fix_div(m):
        plain = unwrap(m.group(2))
        new = plain
        for url, keys in linked:
            for k in keys:
                parts = re.split(r'(<[^>]+>)', new)
                for i, p in enumerate(parts):
                    if p.startswith('<'):
                        continue
                    if k in p:
                        parts[i] = p.replace(k, f'<a href="{url}">{k}</a>', 1)
                        new = ''.join(parts)
                        break
        return m.group(1) + new + m.group(3)
    head = re.sub(r'(<div class="session-refs">)(.*?)(</div>)', fix_div, head, flags=re.S)
    return head + sep + tail, n


def inject_nav(html: str, folder_name: str):
    changed = []
    if "/*reffiles*/" not in html:
        html = html.replace("</head>", CSS + "</head>", 1)
        changed.append("css")
    target = f"{folder_name}/index.html"
    if f'href="{target}"' not in html:
        link = f'<a href="{target}">{TOPBAR_LABEL}</a>'
        for anchor in ['<a href="dependencies.html">Dependencies</a>',
                       '<a href="materials.html">Materials</a>',
                       '<a href="#refs">References</a>']:
            if anchor in html:
                html = html.replace(anchor, anchor + link, 1)
                changed.append("topbar")
                break
        if '<nav class="quicklinks">' in html:
            html = html.replace('</nav>', f'  <a href="{target}">{QUICK_LABEL}</a>\n</nav>', 1)
            changed.append("quicklinks")
    return html, changed


def write_listing(folder: pathlib.Path):
    files = sorted(p for p in folder.iterdir()
                   if p.is_file() and p.name != "index.html" and not p.name.startswith("."))
    rows = []
    for p in files:
        b = p.stat().st_size
        size = f"{b/1e6:.1f} MB" if b >= 1e6 else f"{max(1, round(b/1e3))} KB"
        rows.append(f'<tr><td><a href="{p.name}">{p.name}</a></td><td>{size}</td></tr>')
    body = "\n".join(rows) or '<tr><td colspan="2"><em>Folder is empty.</em></td></tr>'
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Point — Reference Files</title>
<style>
body{{font-family:Georgia,serif;background:#f5efe3;color:#241e16;margin:0;line-height:1.6;}}
header{{background:#14304a;color:#f4ecdc;padding:1.6rem;text-align:center;}}
header a{{color:#f3e6c8;}}
.wrap{{max-width:800px;margin:auto;padding:1.4rem;}}
table{{border-collapse:collapse;width:100%;background:#fffdf6;}}
th,td{{border:1px solid #e3dac8;padding:.45rem .7rem;text-align:left;font-size:.92rem;}}
th{{background:#14304a;color:#f4ecdc;}}
a{{color:#1e6e64;}}
</style></head><body>
<header><h1>Point — Reference Files</h1>
<p><a href="../index.html">← back to syllabus</a></p></header>
<div class="wrap">
<table><tr><th>File</th><th>Size</th></tr>
{body}
</table>
<p style="font-size:.82rem;color:#79705f;margin-top:1rem;">Regenerated by <code>tools/publish_references.py</code>.</p>
</div></body></html>
"""
    (folder / "index.html").write_text(html, encoding="utf-8")
    return len(files)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()

    folder = pick_folder()
    entries, pending, man = load_manifest()
    moved = promote(entries, pending, folder, man)
    for f in moved:
        print(f"  promoted (file found): {f}")

    linked = []
    for e in entries:
        f = resolve_file(folder, e["file"])
        if not f:
            continue
        keys = sorted([k for k in e.get("keys", []) if k], key=len, reverse=True)
        if keys:
            linked.append((f"{folder.name}/{f}", keys))

    html = INDEX.read_text(encoding="utf-8")
    html, n = rebuild(html, linked)
    html, nav = inject_nav(html, folder.name)
    INDEX.write_text(html, encoding="utf-8")
    print(f"index.html: {n} consolidated item(s) linked; session Refs re-linked; nav: {', '.join(nav) or 'ok'}")

    count = write_listing(folder)
    print(f"{folder.name}/index.html written ({count} file(s) listed)")

    git("add", folder.name, "index.html", str(man.relative_to(ROOT)))
    c = git("commit", "-m", f"references: rebuild links ({count} file(s), {len(moved)} promoted)", check=False)
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