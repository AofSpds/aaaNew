"""S3 롤업 시제품: 역할 Current(B안 jsonl 스트림) → 도메인 Current 자동 생성과 이상 표시.

RHS 구조 시뮬레이션(rollup_sim.py @ bc344e2)의 2026-10-17 시나리오를 고정 머리 칸으로 다시
돌려, 그때 드러난 문제(검증자 대기, 가짜 교착, 교차 항목 누락, 풀 사람 없는 엇갈림, 쉬는 역할
경고)가 규칙으로 잡히는지 본다. 이어서 갱신 1만 건에서 쓰기 + view 재생성 시간을 잰다.
표준 라이브러리만 쓴다. 아무것도 지우지 않으므로 out_dir은 아직 없는 새 경로여야 한다.

사용: python -I s3_rollup_proto.py <out_dir>
"""
import datetime as dt
import json
import os
import random
import re
import sys
import time
from pathlib import Path

REQUIRED = ["role", "session", "state", "updated", "now", "next", "waiting_for", "owner_wait"]
OPTIONAL = ["serves", "cross_refs", "base_commit", "in_flight", "body"]
STATES = {"ACTIVE", "WAITING", "BLOCKED", "IDLE", "DONE"}
LIVE = {"ACTIVE", "WAITING", "BLOCKED"}  # 오래됨 경고는 이 상태에만
TARGET = re.compile(r"^(role|verifier|owner|external):\S.*$")

if os.name == "nt":
    import msvcrt

    def _lock(f):
        while True:
            try:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                return
            except OSError:
                time.sleep(0.0005)

    def _unlock(f):
        f.seek(0)
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl

    def _lock(f):
        fcntl.flock(f, fcntl.LOCK_EX)

    def _unlock(f):
        fcntl.flock(f, fcntl.LOCK_UN)


def stream_name(role):
    return role.replace("/", "__") + ".jsonl"


def last_record(path):
    """스트림 끝줄만 읽는다(전체 재생성 없이 최신 판). 줄바꿈 없는 끝줄은 쓰다 만 기록으로 본다."""
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        pos, buf = end, b""
        while pos > 0:
            step = min(4096, pos)
            pos -= step
            f.seek(pos)
            buf = f.read(step) + buf
            if buf.count(b"\n") >= 2 or pos == 0:
                break
    lines = buf.split(b"\n")
    if lines[-1] != b"":
        lines = lines[:-1]  # 쓰다 만 끝줄 제외
    lines = [ln for ln in lines if ln]
    return json.loads(lines[-1]) if lines else None


class Store:
    def __init__(self, root, expected_roles):
        self.root = root
        (root / "streams").mkdir(parents=True)
        (root / "roles.json").write_text(json.dumps(expected_roles, indent=2), encoding="utf-8")
        self.expected = expected_roles

    def set(self, rec, at, stale_h=6):
        """CLI `memo set` 자리: 검사 → 잠금 → 추가 → view 재생성."""
        rec = dict(rec, updated=at.isoformat(timespec="minutes"))
        rec.setdefault("waiting_for", [])
        rec.setdefault("owner_wait", "-")
        missing = [k for k in REQUIRED if k not in rec]
        unknown = [k for k in rec if k not in REQUIRED + OPTIONAL + ["created_by"]]
        bad_targets = [t for t in rec["waiting_for"] if not TARGET.match(t)]
        if missing or unknown or rec.get("state") not in STATES or bad_targets:
            raise ValueError(f"rejected: missing={missing} unknown={unknown} "
                             f"state={rec.get('state')} bad_targets={bad_targets}")
        rec["created_by"] = rec["session"]
        path = self.root / "streams" / stream_name(rec["role"])
        line = json.dumps(rec, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        with open(str(path) + ".lock", "a+b") as lk:
            _lock(lk)
            try:
                with open(path, "a", encoding="utf-8", newline="\n") as f:
                    f.write(line)
            finally:
                _unlock(lk)
        return self.regenerate(at, stale_h)

    def heads(self):
        out = {}
        for p in (self.root / "streams").glob("*.jsonl"):
            r = last_record(p)
            if r:
                out[r["role"]] = r
        return out

    def regenerate(self, at, stale_h):
        heads = self.heads()
        flags = flag(heads, self.expected, at, stale_h)
        lines = [f"# 도메인 CURRENT — 생성 {at:%Y-%m-%d %H:%M} (직접 고치지 않음)", "",
                 "| 역할 | 세션 | 상태 | 지금 | 다음 | 기다리는 대상 | Owner 대기 | 갱신 |", "|---|---|---|---|---|---|---|---|"]
        for role in sorted(heads):
            h = heads[role]
            lines.append(f"| {role} | {h['session']} | {h['state']} | {h['now']} | {h['next']} | "
                         f"{', '.join(h['waiting_for']) or '-'} | {h['owner_wait']} | {h['updated'][11:]} |")
        lines += ["", "## 표시", *([f"- {x}" for x in flags] or ["- 없음"])]
        out = self.root / "views" / "domain" / "current.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        return flags


def flag(heads, expected, at, stale_h):
    flags = []
    for role in expected:
        if role not in heads:
            flags.append(f"MISSING {role}: Current 없음")
    for role, h in sorted(heads.items()):
        age = (at - dt.datetime.fromisoformat(h["updated"])).total_seconds() / 3600
        if h["state"] in LIVE and age > stale_h:
            flags.append(f"STALE {role} ({h['state']} {age:.0f}h) → 확인: {h['session']}")
        for t in h["waiting_for"]:
            kind, ref = t.split(":", 1)
            if kind != "role":
                continue
            if ref not in heads:
                flags.append(f"UNKNOWN_TARGET {role} → {ref}: 그런 역할 없음 → 확인: {h['session']}")
            elif heads[ref]["state"] == "DONE":
                # 엇갈림: 더 오래된 쪽이 풀 책임
                older = role if h["updated"] <= heads[ref]["updated"] else ref
                flags.append(f"CONFLICT {role}가 {ref}를 기다리지만 {ref}는 DONE → 확인: {heads[older]['session']}")
            elif f"role:{role}" in heads[ref]["waiting_for"] and role < ref:
                flags.append(f"CYCLE {role} ↔ {ref} 서로 기다림 → 확인: {h['session']}, {heads[ref]['session']}")
    waits = {}
    for role, h in heads.items():
        for t in h["waiting_for"]:
            if not t.startswith("role:"):
                waits.setdefault(t, []).append(role)
    for t, roles in sorted(waits.items()):
        flags.append(f"WAIT {t} ← {', '.join(sorted(roles))}")
    xs = {}
    for role, h in heads.items():
        for x in h.get("cross_refs", []):
            xs.setdefault(x, set()).add(role.split("/")[1])
    for x, projects in sorted(xs.items()):
        if len(projects) < 2:
            flags.append(f"CROSS_ONE_SIDED {x}: {', '.join(sorted(projects))} 쪽에만 있음")
    return flags


def scenario(out):
    roles = [f"rhs/{p}/{r}" for p in ("order", "sim") for r in ("pln", "arch", "pmo", "rsch")]
    s = Store(out / "scenario", roles)
    T = lambda h, m: dt.datetime(2026, 10, 17, h, m)
    sess = lambda role: role.upper()
    for r in roles:
        s.set({"role": r, "session": sess(r), "state": "IDLE", "now": "seeded", "next": "-"}, T(9, 0))
    s.set({"role": "rhs/order/pmo", "session": "RHS/ORDER/PMO", "state": "ACTIVE", "now": "F2 official run",
           "next": "return to PLN", "serves": "order-P2"}, T(10, 10))
    s.set({"role": "rhs/order/pln", "session": "RHS/ORDER/PLN", "state": "WAITING",
           "now": "F2 returned, ACCEPTED_PENDING_PMOV", "next": "final accept after PMOV H3d",
           "waiting_for": ["verifier:PMOV#H3d"], "serves": "RHS-M1"}, T(11, 9))
    checkpoints = {"11:30": s.regenerate(T(11, 30), 6)}
    s.set({"role": "rhs/sim/pln", "session": "RHS/SIM/PLN", "state": "ACTIVE",
           "now": "E-1 found: spot buy fee in base asset", "next": "tell order PLN",
           "cross_refs": ["RHS-X-001"]}, T(12, 0))
    s.set({"role": "rhs/order/pmo", "session": "RHS/ORDER/PMO", "state": "WAITING", "now": "F2 waiting PMOV H3d",
           "next": "fix if PMOV finds", "waiting_for": ["verifier:PMOV#H3d"]}, T(13, 0))
    checkpoints["13:30"] = s.regenerate(T(13, 30), 6)
    s.set({"role": "rhs/order/pln", "session": "RHS/ORDER/PLN", "state": "WAITING", "now": "PMOV H3d PASS",
           "next": "accept after PMO freeze", "waiting_for": ["role:rhs/order/pmo"]}, T(14, 0))
    s.set({"role": "rhs/order/pmo", "session": "RHS/ORDER/PMO", "state": "DONE", "now": "F2 frozen 4da7fd5",
           "next": "-"}, T(15, 0))
    checkpoints["15:30"] = s.regenerate(T(15, 30), 6)
    checkpoints["23:59"] = s.regenerate(T(23, 59), 6)
    rejected = []
    for bad in ({"role": "rhs/order/pln", "session": "X", "state": "DONE?", "now": "-", "next": "-"},
                {"role": "rhs/order/pln", "session": "X", "state": "WAITING", "now": "-", "next": "-",
                 "waiting_for": ["PMOV"]},
                {"role": "rhs/order/pln", "session": "X", "state": "IDLE", "now": "-", "next": "-", "history": "..."}):
        try:
            s.set(bad, T(23, 59))
        except ValueError as e:
            rejected.append(str(e))
    return checkpoints, rejected


def scale(out, n_roles=20, per_role=500):
    rnd = random.Random(3)
    roles = [f"d/p{i // 4}/{['pln', 'pmo', 'rsch', 'arch'][i % 4]}" for i in range(n_roles)]
    s = Store(out / "scale", roles)
    t0 = dt.datetime(2026, 10, 17)
    times = []
    for i in range(n_roles * per_role):
        r = rnd.choice(roles)
        t = time.perf_counter()
        s.set({"role": r, "session": r.upper(), "state": rnd.choice(sorted(STATES)), "now": "x" * 120,
               "next": "y" * 80, "waiting_for": [f"role:{rnd.choice(roles)}"] if rnd.random() < 0.3 else [],
               "body": "z" * 900}, t0 + dt.timedelta(minutes=i))
        times.append(time.perf_counter() - t)
    times.sort()
    return {"updates": len(times), "set_plus_regen_ms_median": times[len(times) // 2] * 1000,
            "p99_ms": times[int(len(times) * 0.99)] * 1000, "max_ms": times[-1] * 1000}


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=False)
    checkpoints, rejected = scenario(out)
    res = {"checkpoints": checkpoints, "rejected": rejected, "scale": scale(out)}
    (out / "results.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
