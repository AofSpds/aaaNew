import sys, json, os
data = json.load(sys.stdin)
gate = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gate_ok")
if not os.path.exists(gate):
    print("MARKER_GATE=blocked: domain memory not delivered", file=sys.stderr); sys.exit(2)
