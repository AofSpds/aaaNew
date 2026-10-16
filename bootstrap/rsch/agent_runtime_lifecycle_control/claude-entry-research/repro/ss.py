import sys, json, os, time
mode = sys.argv[1] if len(sys.argv) > 1 else "ok"
data = json.load(sys.stdin)
log = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hook_log.jsonl")
with open(log, "a", encoding="utf-8") as f:
    f.write(json.dumps({"t": time.time(), "mode": mode, "event": data.get("hook_event_name"), "source": data.get("source"), "cwd": data.get("cwd"), "session_id": data.get("session_id"), "keys": sorted(data.keys())}) + "\n")
src = data.get("source")
if mode == "ok":
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": f"MARKER_HOOK=delta-{src}. Your workbench is bootstrap/rsch."}}))
elif mode == "plain":
    print(f"MARKER_PLAIN=epsilon-{src}")
elif mode == "exit2":
    print("MARKER_EXIT2_STDERR=zeta", file=sys.stderr); sys.exit(2)
elif mode == "exit1":
    print("MARKER_EXIT1_STDERR=eta", file=sys.stderr); sys.exit(1)
elif mode == "stop":
    print(json.dumps({"continue": False, "stopReason": "MARKER_STOP=theta domain memory unavailable"}))
