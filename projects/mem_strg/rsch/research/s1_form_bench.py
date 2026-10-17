"""S1 저장 형태 실측: 파일(A) / jsonl+SQLite 투영(B) / SQLite 단독(C).

같은 가상 메모 갱신 흐름을 세 형태에 기록하고 쓰기 시간, 파일 수, 크기, 롤업 시간,
Git 백업 크기를 잰다. 표준 라이브러리와 git만 쓴다. 아무것도 지우지 않으므로
out_dir은 아직 없는 새 경로여야 한다.

사용: python -I s1_form_bench.py <out_dir> [--roles 20] [--updates 500] [--backups 5]
"""
import argparse
import json
import os
import random
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path

STATES = ["ACTIVE", "IDLE", "BLOCKED", "RETURNED"]
HEADER = ["role", "session", "state", "updated", "base_commit",
          "now", "next", "blocked", "waiting_for", "owner_wait"]
WORDS = "저장 롤업 아카이브 병합 검증 요청 회신 상태 다음 막힘 기다림 결정 범위 단계 증거 커밋".split()


def make_updates(n_roles, per_role, seed=17):
    rnd = random.Random(seed)
    roles = [f"p{i // 4}_{['pln', 'pmo', 'rsch', 'arch'][i % 4]}" for i in range(n_roles)]
    seq = dict.fromkeys(roles, 0)
    line = lambda n: " ".join(rnd.choice(WORDS) for _ in range(n))
    out = []
    for i in range(n_roles * per_role):
        r = rnd.choice(roles)
        seq[r] += 1
        out.append({
            "role": r, "seq": seq[r], "session": r.upper().replace("_", "/"),
            "state": rnd.choice(STATES), "updated": 1_792_000_000 + i * 60,
            "base_commit": f"{rnd.getrandbits(28):07x}", "now": line(12), "next": line(10),
            "blocked": line(4) if rnd.random() < 0.2 else "-",
            "waiting_for": rnd.choice(roles) if rnd.random() < 0.3 else "-", "owner_wait": "-",
            "body": "\n".join(f"- {line(14)}" for _ in range(8)),
        })
    return out


def render_md(u):
    head = "\n".join(f"- {k}: {u[k]}" for k in HEADER)
    return f"# CURRENT — {u['role']}\n\n{head}\n\n{u['body']}\n"


def parse_header(text):
    d = {}
    for ln in text.splitlines():
        if ln.startswith("- ") and ": " in ln:
            k, v = ln[2:].split(": ", 1)
            if k in HEADER:
                d[k] = v
    return d


def domain_md(rows):
    lines = ["# 도메인 CURRENT", "", "| " + " | ".join(HEADER) + " |", "|" + "---|" * len(HEADER)]
    for r in sorted(rows, key=lambda x: x["role"]):
        lines.append("| " + " | ".join(str(r.get(k, "")) for k in HEADER) + " |")
    return "\n".join(lines) + "\n"


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_views(root, rows):
    for u in rows:
        write_text(root / "views" / u["role"] / "current.md", render_md(u))
    write_text(root / "views" / "domain" / "current.md", domain_md(rows))


class FormA:
    """파일: CURRENT.md 덮어쓰기 + 직전 판을 archive/에 사본 + archive/INDEX.md 한 줄."""
    name, gitignore = "A_files", ""

    def __init__(self, root):
        self.root = root

    def write(self, u):
        d = self.root / "roles" / u["role"]
        cur = d / "CURRENT.md"
        if cur.exists():
            name = f"{u['updated']}_{u['seq'] - 1:05d}_CURRENT.md"
            (d / "archive").mkdir(exist_ok=True)
            shutil.copyfile(cur, d / "archive" / name)
            with open(d / "archive" / "INDEX.md", "a", encoding="utf-8", newline="\n") as f:
                f.write(f"- {name}\n")
        tmp = d / "CURRENT.tmp"
        write_text(tmp, render_md(u))
        os.replace(tmp, cur)

    def rollup(self):
        rows = [parse_header(p.read_text(encoding="utf-8"))
                for p in sorted((self.root / "roles").glob("*/CURRENT.md"))]
        write_text(self.root / "domain" / "CURRENT.md", domain_md(rows))
        return len(rows)

    def before_backup(self):
        pass


class FormB:
    """jsonl 추가 전용(역할별 스트림 1파일) + SQLite 투영(메모리, 재생성) + 생성 view."""
    name, gitignore = "B_jsonl_sqlite", "views/\nindex.sqlite\n"

    def __init__(self, root):
        self.root = root
        (root / "streams").mkdir(parents=True, exist_ok=True)

    def write(self, u):
        rec = json.dumps(u, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        with open(self.root / "streams" / f"{u['role']}.jsonl", "a", encoding="utf-8", newline="\n") as f:
            f.write(rec + "\n")

    def project(self):
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE memo(role TEXT, seq INT, rec TEXT, PRIMARY KEY(role, seq))")
        for p in sorted((self.root / "streams").glob("*.jsonl")):
            with open(p, encoding="utf-8") as f:
                rows = []
                for ln in f:
                    u = json.loads(ln)
                    rows.append((u["role"], u["seq"], ln))
                con.executemany("INSERT INTO memo VALUES(?,?,?)", rows)
        return con

    def rollup(self):
        con = self.project()
        rows = [json.loads(r[0]) for r in con.execute(
            "SELECT rec FROM memo m WHERE seq = (SELECT max(seq) FROM memo WHERE role = m.role)")]
        write_views(self.root, rows)
        con.close()
        return len(rows)

    def before_backup(self):
        pass


class FormC:
    """SQLite 단독(WAL). 갱신 1건 = 트랜잭션 1개. 백업 전 checkpoint 필요."""
    name, gitignore = "C_sqlite", "views/\nmemo.sqlite-wal\nmemo.sqlite-shm\n"

    def __init__(self, root):
        self.root = root
        self.con = sqlite3.connect(root / "memo.sqlite", isolation_level=None)
        self.con.execute("PRAGMA journal_mode=WAL")
        self.con.execute("PRAGMA synchronous=NORMAL")
        self.con.execute("CREATE TABLE memo_rev(role TEXT, seq INT, rec TEXT, PRIMARY KEY(role, seq))")

    def write(self, u):
        self.con.execute("INSERT INTO memo_rev VALUES(?,?,?)",
                         (u["role"], u["seq"], json.dumps(u, ensure_ascii=False, sort_keys=True)))

    def rollup(self):
        rows = [json.loads(r[0]) for r in self.con.execute(
            "SELECT rec FROM memo_rev m WHERE seq = (SELECT max(seq) FROM memo_rev WHERE role = m.role)")]
        write_views(self.root, rows)
        return len(rows)

    def before_backup(self):
        self.con.execute("PRAGMA wal_checkpoint(TRUNCATE)")


def git(root, *args):
    cmd = ["git", "-c", "core.autocrlf=false", "-c", "user.name=bench",
           "-c", "user.email=bench@localhost", *args]
    return subprocess.run(cmd, cwd=root, check=True, capture_output=True,
                          text=True, encoding="utf-8").stdout


def tree_stats(root):
    files = [p for p in root.rglob("*") if p.is_file() and ".git" not in p.relative_to(root).parts]
    return len(files), sum(p.stat().st_size for p in files)


def count_objects(root):
    d = dict(ln.split(": ") for ln in git(root, "count-objects", "-v").splitlines())
    return int(d["size"]) + int(d["size-pack"])  # KiB


def run_form(cls, out, updates, backups):
    root = out / cls.name
    root.mkdir()
    form = cls(root)
    git(root, "init", "-q")
    write_text(root / ".gitignore", cls.gitignore)
    chunk = len(updates) // backups
    res = {"form": cls.name, "write_s": 0.0, "rollup_s": [], "backup": []}
    for k in range(backups):
        part = updates[k * chunk:(k + 1) * chunk]
        t = time.perf_counter()
        for u in part:
            form.write(u)
        res["write_s"] += time.perf_counter() - t
        t = time.perf_counter()
        n = form.rollup()
        res["rollup_s"].append(time.perf_counter() - t)
        form.before_backup()
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", f"backup {k + 1}")
        add = dele = binary = 0
        for ln in git(root, "show", "--numstat", "--format=", "HEAD").splitlines():
            a, d, _ = ln.split("\t", 2)
            if a == "-":
                binary += 1
            else:
                add, dele = add + int(a), dele + int(d)
        res["backup"].append({"files_changed": len(git(root, "show", "--name-only", "--format=", "HEAD").split()),
                              "lines_added": add, "lines_deleted": dele, "binary_files": binary,
                              "git_kib": count_objects(root)})
    res["roles_in_rollup"] = n
    res["files"], res["bytes"] = tree_stats(root)
    git(root, "gc", "-q")
    res["git_kib_after_gc"] = count_objects(root)
    res["write_ms_per_update"] = res["write_s"] * 1000 / (chunk * backups)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--roles", type=int, default=20)
    ap.add_argument("--updates", type=int, default=500, help="역할당 평균 갱신 수")
    ap.add_argument("--backups", type=int, default=5)
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=False)
    updates = make_updates(a.roles, a.updates)
    results = {"params": vars(a), "total_updates": len(updates),
               "forms": [run_form(c, out, updates, a.backups) for c in (FormA, FormB, FormC)]}
    write_text(out / "results.json", json.dumps(results, ensure_ascii=False, indent=2))
    for r in results["forms"]:
        last = r["backup"][-1]
        print(f"{r['form']}: write {r['write_ms_per_update']:.3f} ms/upd, files {r['files']}, "
              f"bytes {r['bytes']}, rollup max {max(r['rollup_s']) * 1000:.1f} ms, "
              f"last backup files_changed {last['files_changed']} +{last['lines_added']}/-{last['lines_deleted']} "
              f"bin {last['binary_files']}, git {last['git_kib']} KiB -> gc {r['git_kib_after_gc']} KiB")


if __name__ == "__main__":
    main()
