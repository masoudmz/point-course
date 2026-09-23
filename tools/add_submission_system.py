#!/usr/bin/env python3
"""Per-session exercise submission system (multi-file: images/PDF), backed by
Supabase (default) or Firebase. Injects a modal + per-session buttons into index.html
and regenerates submissions.html with a LIVE public-submissions list.
Idempotent.  Usage: python tools/add_submission_system.py [--no-push]
"""
import argparse
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = pathlib.Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
CONFIG = TOOLS / "submission_config.json"
SUBS = ROOT / "submissions.html"

CSS = """<style>/*submission-modal*/
.submission-btn{font-size:.72rem;font-weight:700;border:1px solid var(--teal);color:var(--teal);border-radius:10px;padding:.1rem .6rem;margin-left:.5rem;cursor:pointer;background:transparent;}
.submission-btn:hover{background:var(--teal);color:#fff;}
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:9999;justify-content:center;align-items:center;}
.modal-overlay.active{display:flex;}
.modal-box{background:#fffdf6;border-radius:12px;padding:1.6rem;max-width:620px;width:92%;max-height:90vh;overflow-y:auto;box-shadow:0 8px 32px rgba(0,0,0,.3);}
.modal-box h3{margin-top:0;color:var(--navy);}
.modal-box label{display:block;font-weight:600;margin:.7rem 0 .25rem;font-size:.9rem;}
.modal-box input,.modal-box textarea,.modal-box select{width:100%;padding:.5rem;border:1px solid #ccc;border-radius:6px;font-family:inherit;font-size:.9rem;}
.modal-box textarea{min-height:100px;resize:vertical;}
.hint{font-size:.78rem;color:#888;}
.checkbox-row{display:flex;align-items:center;gap:.5rem;margin:.7rem 0;}
.checkbox-row input{width:auto;}
.modal-actions{display:flex;gap:.8rem;justify-content:flex-end;margin-top:1.2rem;}
.modal-actions button{padding:.55rem 1.3rem;border:none;border-radius:6px;font-weight:700;cursor:pointer;}
.btn-cancel{background:#e0e0e0;color:#333;} .btn-submit{background:var(--teal);color:#fff;}
.btn-submit:disabled{opacity:.5;cursor:not-allowed;}
.status-msg{padding:.7rem;border-radius:6px;margin-top:.9rem;font-size:.9rem;}
.status-msg.success{background:#d4edda;color:#155724;}
.status-msg.error{background:#f8d7da;color:#721c24;}
.status-msg.info{background:#fff3cd;color:#856404;}
</style>
"""

MODAL = """<div class="modal-overlay" id="submissionModal">
  <div class="modal-box">
    <h3>Submit solutions — <span id="sub-session-label"></span></h3>
    <form id="submissionForm">
      <input type="hidden" id="sub-session">
      <label for="sub-name">Your name (optional — leave blank for anonymous)</label>
      <input type="text" id="sub-name" autocomplete="off">
      <label for="sub-solution">Notes / solution text (optional)</label>
      <textarea id="sub-solution" placeholder="e.g. which exercises are solved, remarks..."></textarea>
      <label for="sub-file">Files (one or more: photos of handwriting or a typed PDF)</label>
      <input type="file" id="sub-file" accept="image/*,application/pdf" multiple>
      <div class="hint">Images (JPG/PNG/…) or PDF · max 10MB each · multiple files allowed</div>
      <div class="checkbox-row">
        <input type="checkbox" id="sub-public" checked>
        <label for="sub-public" style="margin:0;font-weight:normal;">Make my submission public (visible to everyone)</label>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn-cancel" onclick="closeSubmissionModal()">Cancel</button>
        <button type="submit" class="btn-submit" id="submitBtn">Submit</button>
      </div>
      <div id="statusMsg"></div>
    </form>
  </div>
</div>
"""

JS = r"""<script id="submission-cfg" type="application/json">__CONFIG_JSON__</script>
__SDK_TAGS__
<script>/*submission-modal-js*/
(function(){
const CFG = JSON.parse(document.getElementById('submission-cfg').textContent);
let sb = null, fb = null;
if (CFG.backend === 'supabase') sb = supabase.createClient(CFG.supabase.url, CFG.supabase.anon_key);
if (CFG.backend === 'firebase') { firebase.initializeApp(CFG.firebase); fb = { db: firebase.firestore(), st: firebase.storage() }; }
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function show(kind, msg){ $('statusMsg').innerHTML = '<div class="status-msg '+kind+'">'+esc(msg)+'</div>'; }
window.openSubmissionModal = function(sid){
  $('sub-session').value = sid; $('sub-session-label').textContent = sid;
  $('submissionModal').classList.add('active'); document.body.style.overflow='hidden';
};
window.closeSubmissionModal = function(){
  $('submissionModal').classList.remove('active'); document.body.style.overflow='';
  $('submissionForm').reset(); $('statusMsg').innerHTML='';
};
$('submissionModal').addEventListener('click', e => { if (e.target.classList.contains('modal-overlay')) closeSubmissionModal(); });
const safe = n => n.replace(/[^\\w.\\-]+/g,'_');
async function store(files, isPublic, session){
  const out = [];
  if (CFG.backend === 'supabase') {
    const bucket = isPublic ? 'solutions-public' : 'solutions-private';
    for (const f of files) {
      const path = session + '/' + Date.now() + '-' + safe(f.name);
      const up = await sb.storage.from(bucket).upload(path, f, { upsert: false });
      if (up.error) throw new Error(up.error.message);
      out.push({ bucket, path, name: f.name, size: f.size,
                 url: isPublic ? sb.storage.from(bucket).getPublicUrl(path).publicUrl : null });
    }
    const ins = await sb.from('submissions').insert([{
      session, name: $('sub-name').value.trim() || null,
      solution: $('sub-solution').value.trim() || null, is_public: isPublic, files: out }]);
    if (ins.error) throw new Error(ins.error.message);
  } else {
    const prefix = isPublic ? 'public' : 'private';
    for (const f of files) {
      const ref = fb.st.ref(prefix + '/' + session + '/' + Date.now() + '-' + safe(f.name));
      await ref.put(f);
      out.push({ path: ref.fullPath, name: f.name, size: f.size,
                 url: isPublic ? await ref.getDownloadURL() : null });
    }
    await fb.db.collection('submissions').add({
      session, name: $('sub-name').value.trim() || null,
      solution: $('sub-solution').value.trim() || null, isPublic, files: out, createdAt: Date.now() });
  }
  return out;
}
$('submissionForm').addEventListener('submit', async e => {
  e.preventDefault();
  const session = $('sub-session').value;
  const files = Array.from($('sub-file').files);
  const solution = $('sub-solution').value.trim();
  if (!files.length && !solution) return show('error', 'Add at least one file or a written solution.');
  for (const f of files) {
    if (!(f.type.startsWith('image/') || f.type === 'application/pdf'))
      return show('error', 'Only images or PDF allowed: ' + f.name);
    if (f.size > 10*1024*1024) return show('error', 'File too large (max 10MB): ' + f.name);
  }
  const btn = $('submitBtn'); btn.disabled = true; show('info', 'Uploading…');
  try {
    await store(files, $('sub-public').checked, session);
    show('success', '✓ Submitted — thank you!');
    setTimeout(closeSubmissionModal, 1600);
  } catch (err) { show('error', '✗ ' + err.message); }
  finally { btn.disabled = false; }
});
})();
</script>
"""

SDK_SUPABASE = '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>'
SDK_FIREBASE = ('\n<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js"></script>'
                '\n<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore-compat.js"></script>'
                '\n<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-storage-compat.js"></script>')


def git(*a, check=True):
    return subprocess.run(["git", "-C", str(ROOT), *a], check=check)


def build_submissions_page(cfg):
    js_list = """<script>/*submissions-list-js*/
(function(){
const CFG = JSON.parse(document.getElementById('submission-cfg').textContent);
let sb=null, fb=null;
if (CFG.backend==='supabase') sb=supabase.createClient(CFG.supabase.url, CFG.supabase.anon_key);
if (CFG.backend==='firebase'){ firebase.initializeApp(CFG.firebase); fb=firebase.firestore(); }
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function load(){
  let rows=[];
  if (CFG.backend==='supabase'){
    const r=await sb.from('submissions').select('*').eq('is_public',true).limit(300);
    if (r.error) throw new Error(r.error.message);
    rows=r.data.map(x=>({t:x.created_at,session:x.session,name:x.name,solution:x.solution,files:x.files||[]}));
  } else {
    const snap=await fb.collection('submissions').where('isPublic','==',true).limit(300).get();
    snap.forEach(d=>{const x=d.data();rows.push({t:new Date(x.createdAt||0).toISOString(),session:x.session,name:x.name,solution:x.solution,files:x.files||[]});});
  }
  rows.sort((a,b)=> (b.t||'').localeCompare(a.t||''));
  const tb=document.getElementById('subsBody');
  tb.innerHTML = rows.length ? rows.map(r=>
    '<tr><td>'+esc(r.session)+'</td><td>'+esc(r.name||'Anonymous')+'</td><td>'+esc((r.solution||'').slice(0,120))+'</td><td>'+
    (r.files.filter(f=>f.url).map(f=>'<a href="'+esc(f.url)+'" target="_blank">'+esc(f.name)+'</a>').join('<br>')||'—')+
    '</td><td>'+esc((r.t||'').slice(0,10))+'</td></tr>').join('')
    : '<tr><td colspan="5"><em>No public submissions yet.</em></td></tr>';
}
load().catch(e=>{document.getElementById('subsBody').innerHTML='<tr><td colspan="5">Error: '+esc(e.message)+'</td></tr>';});
})();
</script>"""
    sdk = SDK_SUPABASE if cfg["backend"] == "supabase" else SDK_FIREBASE
    cfg_json = json.dumps(cfg, ensure_ascii=False)
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Point — Submissions</title>
<style>
body{{font-family:Georgia,serif;background:#f5efe3;color:#241e16;margin:0;line-height:1.6;}}
header{{background:#14304a;color:#f4ecdc;padding:1.6rem;text-align:center;}} header a{{color:#f3e6c8;}}
.wrap{{max-width:960px;margin:auto;padding:1.4rem;}}
.intro{{background:#fffdf6;padding:1.1rem;border-radius:8px;border-left:4px solid #1e6e64;margin-bottom:1.4rem;}}
table{{border-collapse:collapse;width:100%;background:#fffdf6;font-size:.88rem;}}
th,td{{border:1px solid #e3dac8;padding:.45rem .6rem;text-align:left;vertical-align:top;}}
th{{background:#14304a;color:#f4ecdc;}}
a{{color:#1e6e64;}}
</style></head><body>
<header><h1>Point — Public Submissions</h1>
<p><a href="index.html">← back to syllabus</a></p></header>
<div class="wrap">
<div class="intro">Solutions that students chose to share. To submit your own, use the
<strong>Submit Solution</strong> button next to any session in the <a href="index.html">syllabus</a>.</div>
<table><thead><tr><th>Session</th><th>By</th><th>Notes</th><th>Files</th><th>Date</th></tr></thead>
<tbody id="subsBody"><tr><td colspan="5"><em>Loading…</em></td></tr></tbody></table>
</div>
<script id="submission-cfg" type="application/json">{cfg_json}</script>
{sdk}
{js_list}
</body></html>
"""
    SUBS.write_text(html, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refresh", action="store_true",
                    help="re-embed the config JSON into index.html and rebuild submissions.html")
    ap.add_argument("--no-push", action="store_true", help="skip the final git push")
    args = ap.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    if args.refresh:
        h = INDEX.read_text(encoding="utf-8")
        h = re.sub(r'(<script id="submission-cfg" type="application/json">).*?(</script>)',
                   lambda m: m.group(1) + json.dumps(cfg, ensure_ascii=False) + m.group(2),
                   h, flags=re.S)
        INDEX.write_text(h, encoding="utf-8")
        build_submissions_page(cfg)
        print("config re-embedded into index.html and submissions.html")
        html = h
    if cfg["backend"] == "supabase" and "XXXX" in cfg["supabase"].get("url", "XXXX"):
        raise SystemExit("error: fill tools/submission_config.json first (supabase url/anon_key or firebase config)")

    html = INDEX.read_text(encoding="utf-8")
    if "/*submission-modal*/" not in html:
        html = html.replace("</head>", CSS + "</head>", 1)
    if 'id="submissionModal"' not in html:
        html = html.replace("</body>", MODAL + "</body>", 1)
    if "/*submission-modal-js*/" not in html:
        sdk = SDK_SUPABASE if cfg["backend"] == "supabase" else SDK_FIREBASE
        js = JS.replace("__CONFIG_JSON__", json.dumps(cfg, ensure_ascii=False)).replace("__SDK_TAGS__", sdk)
        html = html.replace("</body>", js + "</body>", 1)
    for sid in cfg["session_ids"]:
        marker = f"openSubmissionModal('{sid}')"
        if marker in html:
            continue
        html_id = sid if sid.startswith("P") else sid[1:]   # S12 -> 12 ; index.html uses id="s12"
        pat = re.compile(r'(<div class="session" id="s' + re.escape(html_id) + r'">.*?</h3>)', re.S)
        html, n = pat.subn(
            lambda m: m.group(1) +
            f'<button class="submission-btn" onclick="openSubmissionModal(\'{sid}\')">Submit Solution</button>',
            html, count=1)
        if n == 0:
            print(f"warn: session block for {sid} not found")
    INDEX.write_text(html, encoding="utf-8")
    print("index.html: modal + per-session Submit buttons ready")

    build_submissions_page(cfg)
    print("submissions.html: live public list ready")

    git("add", "index.html", "submissions.html")
    c = git("commit", "-m", "site: per-session multi-file submission system (supabase/firebase)", check=False)
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