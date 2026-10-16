import sys, json, os, time
ev = sys.argv[1]
d = json.load(sys.stdin)
log = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mid_log.jsonl")
with open(log, "a", encoding="utf-8") as f:
    f.write(json.dumps({"t": time.time(), "ev": ev, "tool": d.get("tool_name"), "keys": sorted(d.keys()), "stop_active": d.get("stop_hook_active")}) + "\n")
if ev == "PreToolUse":
    if d.get("tool_name") == "Read" and "secret" in json.dumps(d.get("tool_input", {})):
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "MARKER_DENY=mu domain policy: secret.txt is off-limits"}}))
    sys.exit(0)
if ev == "PostToolUse":
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "MARKER_POST=nu (domain note after tool)"}})); sys.exit(0)
if ev == "UserPromptSubmit":
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "MARKER_UPS=xi current task pointer: T-42"}})); sys.exit(0)
if ev == "Stop":
    if not d.get("stop_hook_active"):
        print(json.dumps({"decision": "block", "reason": "MARKER_STOPBLOCK=omicron before finishing, write the single word DONE-OMICRON as your final line."}))
    sys.exit(0)
