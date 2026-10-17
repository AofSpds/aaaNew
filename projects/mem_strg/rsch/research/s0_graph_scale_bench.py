"""S0 그래프 규모 실측: SQLite 재귀 CTE로 출처 추적(위로)·영향 범위(아래로)를 규모별로 잰다.

Codex GRAPH_IMPLEMENTATION_STUDY는 노드 32·관계 40 규모였다. 여기서는 기억 기록이 앞선 기록
1–3개에서 파생되는 DAG(DERIVED_FROM)와, 기록 묶음에서 생성되는 view를 만들고
  ancestors   한 기록의 모든 출처 (깊이 제한 없음)
  impact      원자료 하나가 바뀔 때 다시 계산해야 하는 기록·view 수
를 SQLite만으로 잰다. 전용 그래프 DB가 필요한 규모인지 판단하는 근거로 쓴다.
표준 라이브러리만 쓴다. out_dir은 아직 없는 새 경로여야 한다.

사용: python -I s0_graph_scale_bench.py <out_dir> [--sizes 10000,100000,1000000] [--queries 200]
"""
import argparse
import json
import random
import sqlite3
import statistics
import time
from pathlib import Path

ANCESTORS = """
WITH RECURSIVE up(id) AS (SELECT ? UNION SELECT e.dst FROM edge e JOIN up ON e.src = up.id)
SELECT count(*) - 1 FROM up"""
IMPACT = """
WITH RECURSIVE down(id) AS (SELECT ? UNION SELECT e.src FROM edge e JOIN down ON e.dst = down.id)
SELECT count(*) - 1, sum(n.kind = 'view') FROM down JOIN node n ON n.id = down.id"""


def build(path, n_records, rnd, window=2000):
    con = sqlite3.connect(path)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    con.execute("CREATE TABLE node(id INTEGER PRIMARY KEY, kind TEXT)")
    con.execute("CREATE TABLE edge(src INTEGER, dst INTEGER, kind TEXT)")  # src DERIVED_FROM dst
    n_sources = max(10, n_records // 50)
    nodes = [(i, "source") for i in range(n_sources)]
    edges = []
    for i in range(n_sources, n_sources + n_records):
        nodes.append((i, "record"))
        lo = max(0, i - window)  # 최근 기록에서 주로 파생 (시간 지역성)
        for d in {rnd.randrange(lo, i) for _ in range(rnd.randint(1, 3))}:
            edges.append((i, d, "DERIVED_FROM"))
    n_views = max(5, n_records // 200)
    base = n_sources + n_records
    for v in range(n_views):
        vid = base + v
        nodes.append((vid, "view"))
        for d in {rnd.randrange(n_sources, base) for _ in range(20)}:
            edges.append((vid, d, "SELECTS"))
    con.executemany("INSERT INTO node VALUES(?,?)", nodes)
    con.executemany("INSERT INTO edge VALUES(?,?,?)", edges)
    con.execute("CREATE INDEX e_src ON edge(src)")
    con.execute("CREATE INDEX e_dst ON edge(dst)")
    con.commit()
    return con, n_sources, base, len(nodes), len(edges)


def timed(con, sql, ids):
    ts, outs = [], []
    for i in ids:
        t = time.perf_counter()
        outs.append(con.execute(sql, (i,)).fetchone())
        ts.append((time.perf_counter() - t) * 1000)
    ts.sort()
    return {"median_ms": statistics.median(ts), "p95_ms": ts[int(len(ts) * 0.95)], "max_ms": ts[-1],
            "result_median": statistics.median(o[0] for o in outs)}, outs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--sizes", default="10000,100000,1000000")
    ap.add_argument("--queries", type=int, default=200)
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=False)
    results = []
    for n in map(int, a.sizes.split(",")):
        rnd = random.Random(n)
        t = time.perf_counter()
        con, n_sources, base, n_nodes, n_edges = build(out / f"graph_{n}.sqlite", n, rnd)
        build_s = time.perf_counter() - t
        recent = [rnd.randrange(base - 1000, base) for _ in range(a.queries)]
        anc, _ = timed(con, ANCESTORS, recent)
        srcs = [rnd.randrange(0, n_sources) for _ in range(a.queries)]
        imp, outs = timed(con, IMPACT, srcs)
        imp["views_median"] = statistics.median((o[1] or 0) for o in outs)
        r = {"records": n, "nodes": n_nodes, "edges": n_edges, "build_s": build_s,
             "db_bytes": (out / f"graph_{n}.sqlite").stat().st_size, "ancestors": anc, "impact": imp}
        con.close()
        results.append(r)
        print(json.dumps(r, ensure_ascii=False))
    (out / "results.json").write_text(json.dumps({"params": vars(a), "results": results}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
