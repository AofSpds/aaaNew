import sys, json
json.load(sys.stdin)
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "Domain entry: you are role rsch. Begin every reply with the exact token [WB:rsch] on its own line."}}))
