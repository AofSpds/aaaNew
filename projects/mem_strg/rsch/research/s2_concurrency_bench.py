"""S2 동시 쓰기 실측: 같은 PC에서 프로세스 여럿이 메모를 동시에 기록할 때 손실·손상 여부.

방식 5가지를 같은 조건으로 돌린다. 프로세스는 시작 신호 파일이 생길 때까지 기다렸다가
동시에 기록한다. 기록의 10%는 10 KB(파이썬 버퍼 8 KB를 넘김), 나머지는 1 KB.

  overwrite     파일 하나를 읽고-고치고-통째로 바꿔 씀 (지금의 CURRENT.md 편집 방식)
  append_nolock 같은 jsonl에 잠금 없이 추가
  append_lock   같은 jsonl에 잠금 파일(지우지 않음)로 직렬화해 추가
  per_writer    쓰는 프로세스마다 자기 jsonl에 추가
  sqlite        SQLite WAL 한 파일에 건마다 트랜잭션

표준 라이브러리만 쓴다. 아무것도 지우지 않으므로 out_dir은 아직 없는 새 경로여야 한다.
사용: python -I s2_concurrency_bench.py <out_dir> [--procs 8] [--n 500]
"""
import argparse
import json
import os
import random
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

MODES = ["overwrite", "append_nolock", "append_lock", "per_writer", "sqlite"]

if os.name == "nt":
    import msvcrt

    def try_lock(f):
        f.seek(0)
        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)

    def unlock(f):
        f.seek(0)
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl

    def try_lock(f):
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def unlock(f):
        fcntl.flock(f, fcntl.LOCK_UN)


def append(path, rec):
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(rec)


def worker(mode, path, wid, n, go):
    while not os.path.exists(go):
        time.sleep(0.001)
    rnd = random.Random(wid)
    waits = errors = 0
    con = sqlite3.connect(path, timeout=30, isolation_level=None) if mode == "sqlite" else None
    t = time.perf_counter()
    for i in range(n):
        size = 10_000 if rnd.random() < 0.1 else 1_000
        rec = json.dumps({"w": wid, "i": i, "pad": "가" * (size // 3)}, ensure_ascii=False) + "\n"
        if mode == "overwrite":
            for _ in range(200):
                try:
                    old = Path(path).read_text(encoding="utf-8")
                    tmp = Path(f"{path}.{wid}.tmp")
                    tmp.write_text(old + f"{wid}:{i}\n", encoding="utf-8", newline="\n")
                    os.replace(tmp, path)
                    break
                except PermissionError:
                    waits += 1
                    time.sleep(0.001)
            else:
                errors += 1
        elif mode == "append_nolock":
            append(path, rec)
        elif mode == "append_lock":
            with open(path + ".lock", "a+b") as lk:
                while True:
                    try:
                        try_lock(lk)
                        break
                    except OSError:
                        waits += 1
                        time.sleep(0.0005)
                try:
                    append(path, rec)
                finally:
                    unlock(lk)
        elif mode == "per_writer":
            append(f"{path}.w{wid}.jsonl", rec)
        elif mode == "sqlite":
            for _ in range(50):
                try:
                    con.execute("INSERT INTO t VALUES(?,?,?)", (wid, i, rec))
                    break
                except sqlite3.OperationalError:
                    waits += 1
            else:
                errors += 1
    print(json.dumps({"wid": wid, "waits": waits, "errors": errors, "s": time.perf_counter() - t}))


def check_jsonl(files, procs, n):
    seen, bad, dup = set(), 0, 0
    for p in files:
        with open(p, encoding="utf-8", errors="replace", newline="\n") as f:
            for ln in f:
                try:
                    r = json.loads(ln)
                    key = (r["w"], r["i"])
                except (ValueError, KeyError, TypeError):
                    bad += 1
                    continue
                dup += key in seen
                seen.add(key)
    return {"expected": procs * n, "valid": len(seen), "missing": procs * n - len(seen),
            "bad_lines": bad, "duplicates": dup}


def run_mode(mode, out, procs, n):
    d = out / mode
    d.mkdir()
    path = d / ("memo.sqlite" if mode == "sqlite" else "CURRENT.md" if mode == "overwrite" else "stream.jsonl")
    if mode == "sqlite":
        con = sqlite3.connect(path)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("CREATE TABLE t(w INT, i INT, rec TEXT)")
        con.commit()
        con.close()
    elif mode == "overwrite":
        path.write_text("", encoding="utf-8")
    go = d / "go"
    ps = [subprocess.Popen([sys.executable, "-I", __file__, "--worker", mode, str(path), str(w), str(n), str(go)],
                           stdout=subprocess.PIPE, text=True) for w in range(procs)]
    time.sleep(1.0)
    t = time.perf_counter()
    go.write_text("go")
    reports = [json.loads(p.communicate()[0]) for p in ps]
    res = {"mode": mode, "wall_s": time.perf_counter() - t,
           "waits": sum(r["waits"] for r in reports), "errors": sum(r["errors"] for r in reports)}
    if mode == "overwrite":
        lines = path.read_text(encoding="utf-8").splitlines()
        res.update(expected=procs * n, valid=len(set(lines)), missing=procs * n - len(set(lines)))
    elif mode == "sqlite":
        con = sqlite3.connect(path)
        rows = con.execute("SELECT count(*), count(DISTINCT w * 1000000 + i) FROM t").fetchone()
        con.close()
        res.update(expected=procs * n, valid=rows[1], missing=procs * n - rows[1], duplicates=rows[0] - rows[1])
    else:
        files = sorted(d.glob("stream.jsonl*.jsonl")) if mode == "per_writer" else [path]
        res.update(check_jsonl(files, procs, n))
    return res


def hold_lock(path):
    lk = open(path, "a+b")
    try_lock(lk)
    print("locked", flush=True)
    time.sleep(60)


def kill_release_test(out):
    """잠금을 잡은 프로세스를 강제 종료한 뒤 다른 프로세스가 잠금을 얻기까지 걸린 시간."""
    path = out / "kill_test.lock"
    p = subprocess.Popen([sys.executable, "-I", __file__, "--hold", str(path)], stdout=subprocess.PIPE, text=True)
    assert p.stdout.readline().strip() == "locked"
    with open(path, "a+b") as lk:
        try:
            try_lock(lk)
            held_by_other = False
        except OSError:
            held_by_other = True
        p.kill()
        p.wait()
        t = time.perf_counter()
        while time.perf_counter() - t < 10:
            try:
                try_lock(lk)
                unlock(lk)
                return {"held_while_alive": held_by_other, "released_after_kill_s": time.perf_counter() - t}
            except OSError:
                time.sleep(0.001)
    return {"held_while_alive": held_by_other, "released_after_kill_s": None}


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        _, _, mode, path, wid, n, go = sys.argv
        worker(mode, path, int(wid), int(n), go)
        return
    if len(sys.argv) > 1 and sys.argv[1] == "--hold":
        hold_lock(sys.argv[2])
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--n", type=int, default=500, help="프로세스당 기록 수")
    ap.add_argument("--modes", default=",".join(MODES))
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=False)
    results = [run_mode(m, out, a.procs, a.n) for m in a.modes.split(",") if m]
    kill = kill_release_test(out)
    (out / "results.json").write_text(json.dumps({"params": vars(a), "results": results, "kill_release": kill},
                                                 ensure_ascii=False, indent=2), encoding="utf-8")
    for r in results:
        print(json.dumps(r, ensure_ascii=False))
    print(json.dumps({"kill_release": kill}))


if __name__ == "__main__":
    main()
