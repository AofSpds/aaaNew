"""Bounded, offline parent-memory selection and invalidation study.
No LLM, no source mutation, no package installation, no production integration.
Expected labels and graph edges are researcher-authored, not independent gold.
"""
from __future__ import annotations
import copy
import hashlib
import json
import platform
import sqlite3
import statistics
import sys
import time
from collections import defaultdict, deque
from pathlib import Path

OUT = Path(__file__).resolve().parent
RSCH = OUT.parent.parent
BYUL = Path(r"C:\Users\ms1pk\dev\Byul")
SOURCES = {
    "requirements": RSCH / "requirements/REQUIREMENTS_CODEX.md",
    "parent_memory": RSCH / "Agent_memory/README.md",
    "lessons": RSCH / "Agent_memory/LESSONS_CODEX.md",
    "byul_common": BYUL / "versions/v0.01/memory/110_OWNER_IMPLEMENTATION_IDEA_COMMON_VIEW_THEN_PERSONA_VIEW_AS_OPTIONAL_MULTI_STAGE_PIPELINE_2026-08-23_0548_KST.md",
    "byul_composition": BYUL / "versions/v0.01/memory/97_OWNER_CONFIRMATION_RELATION_COMPOSITION_IS_VIEW_CONDITIONED_2026-08-23_0511_KST.md",
    "byul_refresh": BYUL / "versions/v0.01/memory/119_OWNER_CONFIRMATION_SOURCE_DELETION_REQUIRES_DERIVED_STATE_RECOMPUTATION_FOR_CURRENT_AND_FUTURE_PERSONA_2026-08-23_0608_KST.md",
    "byul_contract": BYUL / "versions/v0.1/MODEL_CONTRACT.md",
}
SPECS = [
    ("domain", "requirements", "기억 전달의 주체는 도메인이다."),
    ("experience", "requirements", "작업 기록과 사용자 정정, 성공·실패 경험을 보존한다."),
    ("relations", "requirements", "사용자 지정 방향은 jevlike 엔진을 기반으로 관계 엔진을 두는 것이다."),
    ("evidence", "parent_memory", "파일 존재, 모델 입력 포함, 실제 준수, 다음 작업의 효과를 따로 확인한다."),
    ("common", "byul_common", '> "모든 소스를 그대로 볼수는 없고'),
    ("composition", "byul_composition", "The Owner confirms that the immediately preceding question"),
    ("recompute", "byul_refresh", "if a user deletes a Source datum/relation"),
    ("prototype", "byul_contract", "v0.1은 source file을 실제 수정하지 않고 virtual mutation"),
    ("execution", "requirements", "인증 방식과 실행기 선택은 구분한다."),
    ("ui", "requirements", "사용자가 코드를 직접 편집하지 않더라도 사이드바"),
    ("installation", "parent_memory", "| OMP Oh My Pi |"),
    ("completion", "lessons", "| Claude 조사 완료 통보를 받았지만"),
]
EXPECTED = {
    "memory_start": {"domain", "experience", "relations", "evidence", "completion"},
    "graph_design": {"relations", "evidence", "common", "composition", "recompute", "prototype"},
    "graph_refresh": {"recompute", "prototype", "evidence"},
    "runtime_handoff": {"domain", "execution", "evidence"},
    "ui_scope": {"ui"},
}
SELECT_TYPES = {"SELECTS", "INCLUDES"}
DEPENDENCY_TYPES = SELECT_TYPES | {"DERIVED_FROM", "QUERIED", "COMPOSED_FROM"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_cards(raw_overrides=None):
    raw_overrides = raw_overrides or {}
    source_data = {}
    for sid, path in SOURCES.items():
        raw = raw_overrides[sid] if sid in raw_overrides else path.read_bytes()
        source_data[sid] = {"path": str(path), "sha256": sha(raw),
                            "raw_bytes": len(raw), "lines": raw.decode("utf-8-sig").splitlines()}
    cards = {}
    for mid, sid, needle in SPECS:
        lines = source_data[sid]["lines"]
        matches = [i for i, line in enumerate(lines) if needle in line]
        if len(matches) != 1:
            raise ValueError(f"Expected one source span for {mid}, found {len(matches)}")
        start = matches[0]
        end = start + 1
        # Keep the complete paragraph; source scope and provenance remain alongside it.
        while end < len(lines) and lines[end].strip():
            end += 1
        excerpt = "\n".join(lines[start:end])
        cards[mid] = {"id": mid, "text": excerpt, "source": sid,
                      "source_path": source_data[sid]["path"], "lines": [start + 1, end],
                      "source_sha256": source_data[sid]["sha256"],
                      "span_sha256": sha(excerpt.encode("utf-8")),
                      "evidence_class": "source_excerpt_for_research_not_universal_rule"}
    return cards, source_data


class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def node(self, key, kind, version="1"):
        self.nodes[key] = {"kind": kind, "version": version, "active": True}

    def edge(self, consumer, dependency, kind):
        if consumer not in self.nodes or dependency not in self.nodes:
            raise ValueError("Dangling graph edge")
        self.edges.append((consumer, dependency, kind))

    def bump(self, key):
        self.nodes[key]["version"] = sha((self.nodes[key]["version"] + ":simulated-change").encode())

    def trace(self, task):
        root = "t:" + task
        if root not in self.nodes:
            raise ValueError("UNKNOWN_TASK")
        adjacency = defaultdict(list)
        for a, b, kind in self.edges:
            if kind in SELECT_TYPES:
                adjacency[a].append(b)
        paths = {root: [root]}
        queue = deque([root])
        while queue:
            current = queue.popleft()
            for nxt in adjacency[current]:
                if nxt not in paths:
                    paths[nxt] = paths[current] + [nxt]
                    queue.append(nxt)
        return paths

    def select(self, task):
        return {n[2:] for n in self.trace(task) if self.nodes[n]["kind"] == "memory"}

    def affected_views(self, changed):
        reverse = defaultdict(list)
        for a, b, kind in self.edges:
            if kind in DEPENDENCY_TYPES:
                reverse[b].append(a)
        visited = set(changed)
        queue = deque(changed)
        edge_visits = 0
        while queue:
            current = queue.popleft()
            for consumer in reverse[current]:
                edge_visits += 1
                if consumer not in visited:
                    visited.add(consumer)
                    queue.append(consumer)
        views = {n for n in visited if self.nodes[n]["kind"] == "view"}
        return views, {"visited_nodes": len(visited), "followed_edges": edge_visits}


def make_graph(cards, sources):
    g = Graph()
    for sid, source in sources.items():
        g.node("s:" + sid, "source", source["sha256"])
    for mid, card in cards.items():
        g.node("m:" + mid, "memory", card["span_sha256"])
        g.edge("m:" + mid, "s:" + card["source"], "DERIVED_FROM")
    g.node("g:core", "group")
    g.node("g:graph", "group")
    for mid in ("domain", "experience", "relations"):
        g.edge("g:core", "m:" + mid, "INCLUDES")
    for mid in ("relations", "evidence", "common", "composition", "recompute", "prototype"):
        g.edge("g:graph", "m:" + mid, "INCLUDES")
    assignments = {
        "memory_start": ["g:core", "m:evidence", "m:completion"],
        "graph_design": ["g:graph"],
        "graph_refresh": ["m:recompute", "m:prototype", "m:evidence"],
        "runtime_handoff": ["m:domain", "m:execution", "m:evidence"],
        "ui_scope": ["m:ui"],
    }
    for task, deps in assignments.items():
        g.node("t:" + task, "task")
        for dep in deps:
            g.edge("t:" + task, dep, "SELECTS")
        g.node("v:" + task, "view")
        g.edge("v:" + task, "t:" + task, "QUERIED")
    g.node("v:parent_brief", "view")
    g.edge("v:parent_brief", "v:memory_start", "COMPOSED_FROM")
    g.edge("v:parent_brief", "v:graph_design", "COMPOSED_FROM")
    # Mere mention is not a selection or invalidation dependency.
    g.edge("g:graph", "m:installation", "MENTIONS")
    return g


def relational_store(g):
    db = sqlite3.connect(":memory:")
    db.executescript("""
      CREATE TABLE node(id TEXT PRIMARY KEY, kind TEXT, version TEXT);
      CREATE TABLE edge(consumer TEXT, dependency TEXT, kind TEXT);
      CREATE INDEX by_consumer ON edge(consumer,kind);
      CREATE INDEX by_dependency ON edge(dependency,kind);
      CREATE TABLE task_memory(task TEXT, memory TEXT, PRIMARY KEY(task,memory));
    """)
    db.executemany("INSERT INTO node VALUES(?,?,?)", [(k,v["kind"],v["version"]) for k,v in g.nodes.items()])
    db.executemany("INSERT INTO edge VALUES(?,?,?)", g.edges)
    # Strong flat baseline: materialize the SAME task membership once at this snapshot.
    for task in EXPECTED:
        db.executemany("INSERT INTO task_memory VALUES(?,?)", [(task, m) for m in g.select(task)])
    db.commit()
    return db


def select_recursive_sql(db, task):
    if not db.execute("SELECT 1 FROM node WHERE id=?", ("t:" + task,)).fetchone():
        raise ValueError("UNKNOWN_TASK")
    rows = db.execute("""
      WITH RECURSIVE reached(id) AS (
        SELECT ?
        UNION
        SELECT e.dependency FROM edge e JOIN reached r ON e.consumer=r.id
        WHERE e.kind IN ('SELECTS','INCLUDES')
      )
      SELECT n.id FROM node n JOIN reached r ON n.id=r.id WHERE n.kind='memory'
    """, ("t:" + task,))
    return {r[0][2:] for r in rows}


def materialize(g, task, cards):
    paths = g.trace(task)
    selected = g.select(task)
    # Manifest records actually consumed sources independently of dependency-edge existence.
    dependencies = set(paths) | {"s:" + cards[m]["source"] for m in selected}
    inactive = sorted(n for n in dependencies if not g.nodes[n]["active"])
    if inactive:
        return {"state": "BLOCKED", "reason": "inactive_source", "nodes": inactive}
    stale = sorted(m for m in selected
                   if cards[m]["source_sha256"] != g.nodes["s:" + cards[m]["source"]]["version"]
                   or cards[m]["span_sha256"] != sha(cards[m]["text"].encode("utf-8"))
                   or cards[m]["span_sha256"] != g.nodes["m:" + m]["version"])
    if stale:
        return {"state": "BLOCKED", "reason": "source_or_memory_revision_mismatch", "memories": stale}
    return {"state": "READY", "selected": sorted(selected),
            "versions": {n: g.nodes[n]["version"] for n in sorted(dependencies)},
            "traces": {m: paths["m:" + m] + ["s:" + cards[m]["source"]] for m in sorted(selected)}}


def cache_views(g, cards):
    cache = {"v:" + task: materialize(g, task, cards) for task in EXPECTED}
    versions = {}
    selected = set()
    for vid in ("v:memory_start", "v:graph_design"):
        versions.update(cache[vid]["versions"])
        versions[vid] = g.nodes[vid]["version"]
        selected.update(cache[vid]["selected"])
    cache["v:parent_brief"] = {"state": "READY", "versions": versions, "selected": sorted(selected)}
    return cache


def serve(g, packet):
    if packet["state"] != "READY":
        return "BLOCKED"
    for node, expected_version in packet["versions"].items():
        if node not in g.nodes or not g.nodes[node]["active"] or g.nodes[node]["version"] != expected_version:
            return "BLOCKED"
    return "READY"


def payload_bytes(cards, selected):
    # Same serialization for all methods, excluding optional graph path explanations.
    payload = [{k: cards[mid][k] for k in ("id", "text", "source_path", "lines", "source_sha256")}
               for mid in sorted(selected)]
    return len(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def run():
    cards, sources = load_cards()
    g = make_graph(cards, sources)
    db = relational_store(g)
    cache = cache_views(g, cards)
    query_results = []
    functions = {
        "full_packet": lambda task: set(cards),
        "flat_task_mapping": lambda task: {r[0] for r in db.execute("SELECT memory FROM task_memory WHERE task=?", (task,))},
        "typed_graph": g.select,
        "sqlite_recursive_graph": lambda task: select_recursive_sql(db, task),
    }
    for task, expected in EXPECTED.items():
        for method, fn in functions.items():
            actual = fn(task)
            query_results.append({"task": task, "method": method, "selected": sorted(actual),
                "expected": sorted(expected), "true_positive": len(actual & expected),
                "returned": len(actual), "required": len(expected),
                "missing": sorted(expected - actual), "extra": sorted(actual - expected),
                "payload_utf8_bytes": payload_bytes(cards, actual)})
    aggregates = {}
    for method in functions:
        rows = [r for r in query_results if r["method"] == method]
        tp, returned, required = (sum(r[key] for r in rows) for key in ("true_positive", "returned", "required"))
        aggregates[method] = {"precision": tp/returned, "recall": tp/required,
            "returned_cards": returned, "required_cards": required,
            "payload_utf8_bytes": sum(r["payload_utf8_bytes"] for r in rows)}
    controls = []
    def check(name, actual, expected):
        controls.append({"name": name, "actual": actual, "expected": expected, "passed": actual == expected})

    check("all_selection_methods_match_same_policy", all(not r["missing"] and not r["extra"]
          for r in query_results if r["method"] != "full_packet"), True)
    check("trace_contains_query_and_source", all(p[0].startswith("t:") and p[-1].startswith("s:")
          for packet in cache.values() for p in packet.get("traces", {}).values()), True)
    check("mentions_does_not_select_installation", "installation" in g.select("graph_design"), False)
    try:
        g.select("unknown_task")
        unknown = "READY"
    except ValueError:
        unknown = "BLOCKED"
    check("unknown_task_is_not_silently_filled", unknown, "BLOCKED")

    changed = {"s:byul_common"}
    impacts, visits = g.affected_views(changed)
    expected_impacts = ["v:graph_design", "v:parent_brief"]
    check("transitive_update_impact", sorted(impacts), expected_impacts)
    scan_impacts = {vid for vid, packet in cache.items() if changed & packet["versions"].keys()}
    check("flat_manifest_scan_matches_graph", sorted(scan_impacts), expected_impacts)
    changed_graph = copy.deepcopy(g)
    changed_graph.bump("s:byul_common")
    check("lost_invalidation_notice_blocked_by_manifest", serve(changed_graph, cache["v:graph_design"]), "BLOCKED")
    check("unaffected_view_remains_ready", serve(changed_graph, cache["v:ui_scope"]), "READY")
    stale_rebuild = materialize(changed_graph, "graph_design", cards)
    check("version_relabel_without_reextract_is_blocked", stale_rebuild["state"], "BLOCKED")
    # A clearly marked in-memory source variant tests re-extraction without touching originals.
    original_raw = SOURCES["byul_common"].read_bytes()
    assert sha(original_raw) == sources["byul_common"]["sha256"]
    original_text = original_raw.decode("utf-8-sig")
    marker = " [VIRTUAL STUDY CHANGE ONLY]"
    assert original_text.count(cards["common"]["text"]) == 1
    virtual_text = original_text.replace(cards["common"]["text"], cards["common"]["text"] + marker)
    virtual_cards, virtual_sources = load_cards({"byul_common": virtual_text.encode("utf-8")})
    refreshed_graph = copy.deepcopy(g)
    refreshed_graph.nodes["s:byul_common"]["version"] = virtual_sources["byul_common"]["sha256"]
    check("new_source_with_old_memory_version_is_blocked",
          materialize(refreshed_graph, "graph_design", virtual_cards)["state"], "BLOCKED")
    refreshed_graph.nodes["m:common"]["version"] = virtual_cards["common"]["span_sha256"]
    rebuilt = materialize(refreshed_graph, "graph_design", virtual_cards)
    check("virtual_source_is_reextracted", marker in virtual_cards["common"]["text"], True)
    check("coherent_rebuilt_manifest_ready", serve(refreshed_graph, rebuilt), "READY")
    deleted_graph = copy.deepcopy(g)
    deleted_graph.nodes["s:byul_common"]["active"] = False
    check("deleted_source_blocks_cached_packet", serve(deleted_graph, cache["v:graph_design"]), "BLOCKED")
    check("deleted_required_source_blocks_rebuild", materialize(deleted_graph, "graph_design", cards)["state"], "BLOCKED")
    membership_graph = copy.deepcopy(g)
    membership_graph.edge("g:graph", "m:ui", "INCLUDES")
    membership_graph.bump("g:graph")
    check("new_membership_invalidates_old_selection", serve(membership_graph, cache["v:graph_design"]), "BLOCKED")
    check("new_membership_included_after_reselection", "ui" in membership_graph.select("graph_design"), True)
    cycle_graph = copy.deepcopy(g)
    cycle_graph.edge("g:graph", "t:graph_design", "INCLUDES")
    check("cycle_terminates_without_duplicate_items", sorted(cycle_graph.select("graph_design")), sorted(EXPECTED["graph_design"]))
    cycle_db = relational_store(cycle_graph)
    check("sql_union_cycle_terminates", sorted(select_recursive_sql(cycle_db, "graph_design")), sorted(EXPECTED["graph_design"]))
    cycle_db.close()

    # Faults that graph structure alone cannot detect. Record, do not hide as successes.
    missing = copy.deepcopy(g)
    missing.edges.remove(("g:graph", "m:common", "INCLUDES"))
    missing_packet = materialize(missing, "graph_design", cards)
    wrong = copy.deepcopy(g)
    wrong.edge("g:graph", "m:installation", "INCLUDES")
    limitations = [
        {"fault": "omitted_relevance_edge", "missing": sorted(EXPECTED["graph_design"] - missing.select("graph_design")),
         "internal_gate": serve(missing, missing_packet), "recall": len(missing.select("graph_design") & EXPECTED["graph_design"])/len(EXPECTED["graph_design"]),
         "meaning": "Version freshness does not prove semantic coverage."},
        {"fault": "wrongly_typed_selection_edge", "extra": sorted(wrong.select("graph_design") - EXPECTED["graph_design"]),
         "meaning": "Correct traversal can faithfully reproduce a wrong relationship judgment."},
    ]
    # Conservative whole-file revision granularity causes broad invalidation.
    coarse, _ = g.affected_views({"s:parent_memory"})
    check("all_sources_unchanged_after_read_only_study", all(sha(Path(s["path"]).read_bytes()) == s["sha256"] for s in sources.values()), True)
    timings = {}
    for method in ("flat_task_mapping", "typed_graph", "sqlite_recursive_graph"):
        samples = []
        fn = functions[method]
        for _ in range(200):
            start = time.perf_counter_ns()
            for task in EXPECTED:
                fn(task)
            samples.append((time.perf_counter_ns()-start)/len(EXPECTED)/1000)
        timings[method] = {"median_us_per_query": statistics.median(samples), "samples": 200,
                           "scope": "warm in-process selection only; excludes ingestion, index build, disk, LLM, tracing, concurrency"}
    dataset = {"label_status": "researcher_curated_not_independent_gold", "cards": cards,
               "sources": {sid:{k:v for k,v in s.items() if k != "lines"} for sid,s in sources.items()},
               "nodes": g.nodes, "edges": g.edges,
               "expected": {k: sorted(v) for k,v in EXPECTED.items()}}
    result = {"environment": {"python": sys.version, "sqlite": sqlite3.sqlite_version, "platform": platform.platform()},
        "scope": "selection/provenance/invalidation control only; no LLM, no source writes, no crash/concurrency integration",
        "dataset": {"cards": len(cards), "source_files": len(sources), "queries": len(EXPECTED), "cached_views": len(cache),
                    "nodes": len(g.nodes), "edges": len(g.edges), "label_status": dataset["label_status"]},
        "aggregates": aggregates, "queries": query_results,
        "example_selection_traces": cache["v:graph_design"],
        "invalidation": {"changed": sorted(changed), "affected": sorted(impacts),
                         "total_cached_views": len(cache), "graph_walk": visits,
                         "flat_manifest_scan": {"views_scanned": len(cache), "affected": sorted(scan_impacts)},
                         "parent_readme_whole_file_change_affected": sorted(coarse)},
        "virtual_refresh": {"status": "simulation_only_originals_unchanged",
            "memory": "common", "new_text": virtual_cards["common"]["text"],
            "new_source_sha256": virtual_cards["common"]["source_sha256"],
            "new_span_sha256": virtual_cards["common"]["span_sha256"],
            "old_excerpt_rebuild": stale_rebuild, "rebuilt_state": serve(refreshed_graph, rebuilt)},
        "controls": controls, "known_limitations_observed": limitations, "timings": timings,
        "interpretation_limits": [
            "All relevance memberships and expected sets were manually curated from a small known corpus.",
            "Flat mapping is pre-materialized from the same relationships: equal quality is expected, not independent discovery.",
            "Version-only change is a fault injection; it must block old source excerpts from being relabeled as current.",
            "A marked in-memory source variant was re-extracted; semantic summarization quality and end-user task success were not tested.",
            "SQLite uses an in-memory database. No dedicated graph database was installed or compared.",
            "Manifest checking only guards this prototype serve() function, not a real CLI/model call or a competing writer.",
            "File-wide digests are conservative and may invalidate unrelated excerpts in the same file.",
        ]}
    for filename, value in (("dataset.json",dataset),("results.json",result)):
        (OUT/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    db.close()
    failed = [c for c in controls if not c["passed"]]
    print(json.dumps({"dataset": result["dataset"], "aggregates": aggregates,
        "controls_passed": len(controls)-len(failed), "controls_total": len(controls), "failures": failed,
        "invalidation": result["invalidation"], "observed_limitations": limitations, "timings": timings},ensure_ascii=False,indent=2))
    if failed:
        raise SystemExit(1)

if __name__ == "__main__":
    run()
