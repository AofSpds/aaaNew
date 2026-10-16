import json, sys, glob, os
# usage: tx.py <session_id> <out>
sid, out = sys.argv[1], sys.argv[2]
paths = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{sid}.jsonl"))
lines = []
for l in open(paths[0], encoding="utf-8"):
    x = json.loads(l)
    t = x.get("type")
    s = json.dumps(x, ensure_ascii=False)
    a = x.get("attachment") or {}
    if t in ("user", "assistant", "system", "attachment", "summary") or "MARKER_" in s:
        msg = x.get("message") or {}
        content = msg.get("content") if isinstance(msg, dict) else None
        if isinstance(content, list):
            content = " | ".join((c.get("text") or c.get("type", "")) if isinstance(c, dict) else str(c) for c in content)
        lines.append(f"[{t}/{x.get('subtype','')}/{a.get('type','')}] meta={x.get('isMeta','')} compact={x.get('isCompactSummary','')} :: "
                     + (str(content)[:600] if content else s[:600]))
open(out, "w", encoding="utf-8").write(paths[0] + "\n" + "\n".join(lines))
