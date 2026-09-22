#!/usr/bin/env python3
"""Fix mobile rendering of combining macrons (e.g., ℚ̄, K̄) by replacing 
them with robust HTML/CSS spans. Idempotent and safe to re-run.
Usage: python tools/fix_mobile_math.py
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

CSS = """<style>/*mobile-math-fix*/
.math-bar {
  display: inline-block;
  position: relative;
  line-height: 1;
  vertical-align: baseline;
}
.math-bar::before {
  content: "";
  position: absolute;
  top: -0.15em;    /* Height of the bar above the letter */
  left: -0.05em;
  right: -0.05em;
  height: 0.08em;  /* Thickness of the bar */
  background-color: currentColor;
  border-radius: 1px;
}
</style>
"""

def git(*args, check=True):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=check)

def main():
    if not INDEX.exists():
        print(f"Error: {INDEX} not found.", file=sys.stderr)
        sys.exit(1)

    html = INDEX.read_text(encoding="utf-8")
    changes_made = 0

    # 1. Inject CSS if not already present
    if "/*mobile-math-fix*/" not in html:
        html = html.replace("</head>", CSS + "</head>", 1)
        changes_made += 1

    # 2. Replace broken Unicode combining sequences with robust spans
    # ℚ̄ = \u211a (ℚ) + \u0304 (combining macron)
    # K̄ = \u004b (K) + \u0304 (combining macron)
    replacements = {
        "\u211a\u0304": '<span class="math-bar">ℚ</span>',
        "\u004b\u0304": '<span class="math-bar">K</span>',
    }

    for bad, good in replacements.items():
        if bad in html:
            count = html.count(bad)
            html = html.replace(bad, good)
            changes_made += count
            print(f"Replaced {count} instance(s) of '{bad}' with robust HTML.")

    if changes_made == 0:
        print("No changes needed: mobile math fix already applied.")
        return

    INDEX.write_text(html, encoding="utf-8")
    print("index.html updated successfully.")

    # Git commit
    git("add", "index.html")
    c = git("commit", "-m", "fix: robust CSS overline for ℚ̄ and K̄ to prevent mobile rendering issues", check=False)
    if c.returncode != 0:
        print("      (nothing new to commit)")
    
    p = git("push", check=False)
    if p.returncode != 0:
        print("warn: push failed (offline?). Commit is local; push later with: git push")
    
    print("Done. Test on your mobile device (remember to hard-refresh/Ctrl+F5).")

if __name__ == "__main__":
    main()