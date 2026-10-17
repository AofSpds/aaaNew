"""참조값과 백업·복원 실측: 브랜치 묶음을 봉인하고, 참조값만으로 빈 폴더에 복원해 지문을 대조한다.

시험 자료로 work/<브랜치>/<역할>/ 묶음을 만든다. 그다음 다음 순서를 따른다.
  1) manifest(경로·크기·sha256)와 지문 계산
  2) archive 봉인 사본 + 백업 사본 만들기 (읽기 전용 표시)
  3) PR에 넣을 참조값 블록 만들기
  4) 참조값만 보고 빈 폴더에 복원해 대조
고장 5가지를 넣어 대조가 잡아내는지도 본다:
  내용 1바이트 변경 · 파일 누락 · 파일 추가 · 봉인 뒤 jsonl 줄 추가 · manifest 변조
표준 라이브러리만 쓴다. 아무것도 지우지 않으므로 out_dir은 아직 없는 새 경로여야 한다.

사용: python -I backup_restore_bench.py <out_dir>
"""
import hashlib
import json
import os
import shutil
import stat
import sys
import time
from pathlib import Path

ROLES = ["pln", "pmo", "rsch"]


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def make_bundle(work, rnd_seed=7):
    import random
    rnd = random.Random(rnd_seed)
    for r in ROLES:
        d = work / r
        d.mkdir(parents=True)
        with open(d / "memo.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for i in range(200):
                f.write(json.dumps({"role": r, "seq": i + 1, "now": f"작업 {i}", "next": "-"},
                                   ensure_ascii=False, sort_keys=True) + "\n")
        (d / "notes.md").write_text(f"# {r} 노트\n\n- 시험 메모\n", encoding="utf-8", newline="\n")
        (d / "test-data").mkdir()
        for k in range(5):
            (d / "test-data" / f"sample_{k}.bin").write_bytes(rnd.randbytes(20_000))


def manifest_lines(root):
    lines = []
    for p in sorted(root.rglob("*"), key=lambda x: x.relative_to(root).as_posix()):
        if p.is_file():
            rel = p.relative_to(root).as_posix()
            lines.append(f"{rel}\t{p.stat().st_size}\t{sha256_file(p)}")
    return lines


def write_manifest(root, path):
    text = "\n".join(manifest_lines(root)) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest(), len(text.splitlines())


def copy_readonly(src, dst):
    shutil.copytree(src, dst)
    for p in dst.rglob("*"):
        if p.is_file():
            os.chmod(p, stat.S_IREAD)


def verify(restored, manifest_path, expected_manifest_sha):
    """복원본을 manifest와 대조한다. 반환: 문제 목록(빈 목록이면 완전 일치)."""
    problems = []
    raw = manifest_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_manifest_sha:
        problems.append("manifest 지문 불일치 (manifest 변조 또는 다른 묶음)")
    expected = {}
    for ln in raw.decode("utf-8").splitlines():
        rel, size, digest = ln.split("\t")
        expected[rel] = (int(size), digest)
    actual = {p.relative_to(restored).as_posix(): p for p in restored.rglob("*") if p.is_file()}
    for rel, (size, digest) in expected.items():
        p = actual.get(rel)
        if p is None:
            problems.append(f"누락: {rel}")
        elif p.stat().st_size != size:
            problems.append(f"크기 다름: {rel}")
        elif sha256_file(p) != digest:
            problems.append(f"내용 다름: {rel}")
    for rel in sorted(set(actual) - set(expected)):
        problems.append(f"목록에 없는 파일: {rel}")
    return problems


def restore(ref, backup_root, dest):
    src = backup_root / ref["bundle_id"].replace("/", "__").replace("@", "@")
    shutil.copytree(src / "bundle", dest)
    return src / "MANIFEST.tsv"


def writable(root):
    for p in root.rglob("*"):
        if p.is_file():
            os.chmod(p, stat.S_IREAD | stat.S_IWRITE)


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=False)
    branch, head = "feat-f3", "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
    work = out / "store" / "rhs" / "projects" / "order" / "work" / branch
    make_bundle(work)
    t = time.perf_counter()
    bundle_id = f"rhs/order/{branch}@{head[:7]}"
    key = bundle_id.replace("/", "__")
    archive = out / "store" / "rhs" / "archive" / "order" / f"{branch}@{head[:7]}"
    archive.mkdir(parents=True)
    manifest_sha, n_files = write_manifest(work, archive / "MANIFEST.tsv")
    copy_readonly(work, archive / "bundle")
    seal_problems = verify(archive / "bundle", archive / "MANIFEST.tsv", manifest_sha)
    backup_root = out / "backup"
    (backup_root / key).mkdir(parents=True)
    shutil.copy2(archive / "MANIFEST.tsv", backup_root / key / "MANIFEST.tsv")
    copy_readonly(work, backup_root / key / "bundle")
    backup_problems = verify(backup_root / key / "bundle", backup_root / key / "MANIFEST.tsv", manifest_sha)
    seal_s = time.perf_counter() - t
    total_bytes = sum(int(ln.split("\t")[1]) for ln in (archive / "MANIFEST.tsv").read_text(encoding="utf-8").splitlines())
    ref = {"format": "MEMSTORE_REF v1", "store_id": "test-store", "bundle_id": bundle_id,
           "sealed_by": "RHS/ORDER/PLN", "source_commit": head, "roles": ROLES,
           "files": n_files, "bytes": total_bytes, "manifest_sha256": manifest_sha, "backup": "backup-local-1"}
    ref_block = "\n".join(f"{k}: {', '.join(v) if isinstance(v, list) else v}" for k, v in ref.items())
    (out / "PR_REFERENCE_BLOCK.txt").write_text(ref_block + "\n", encoding="utf-8", newline="\n")

    results = {"seal": {"seconds": seal_s, "files": n_files, "bytes": total_bytes,
                        "archive_check": seal_problems, "backup_check": backup_problems}}
    t = time.perf_counter()
    clean = out / "restore_clean"
    m = restore(ref, backup_root, clean)
    results["restore_clean"] = {"seconds": time.perf_counter() - t, "problems": verify(clean, m, manifest_sha)}

    faults = {}
    for name in ["byte_changed", "file_missing", "file_added", "jsonl_appended_after_seal", "manifest_tampered"]:
        dest = out / f"restore_{name}"
        m = restore(ref, backup_root, dest)
        writable(dest)
        target = dest / "pmo" / "memo.jsonl"
        if name == "byte_changed":
            b = bytearray((dest / "rsch" / "test-data" / "sample_2.bin").read_bytes())
            b[100] ^= 1
            (dest / "rsch" / "test-data" / "sample_2.bin").write_bytes(bytes(b))
        elif name == "file_missing":
            os.replace(dest / "pln" / "notes.md", out / f"moved_out_{name}_notes.md")  # 지우지 않고 밖으로 옮김
        elif name == "file_added":
            (dest / "pln" / "extra.txt").write_text("추가", encoding="utf-8")
        elif name == "jsonl_appended_after_seal":
            with open(target, "a", encoding="utf-8", newline="\n") as f:
                f.write('{"role":"pmo","seq":201}\n')
        elif name == "manifest_tampered":
            fake = out / f"manifest_{name}.tsv"
            text = m.read_text(encoding="utf-8").replace("\t", "\t", 1)
            fake.write_text(text.rstrip("\n") + "\nfake.txt\t1\t" + "0" * 64 + "\n", encoding="utf-8", newline="\n")
            m = fake
        faults[name] = verify(dest, m, manifest_sha)
    results["faults_detected"] = {k: (len(v) > 0, v) for k, v in faults.items()}
    (out / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(ref_block)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
