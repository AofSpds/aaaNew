"""참조값과 백업·복원 실측 v2 — Pro P3 검토를 반영해 v1(backup_restore_bench.py)의 결함을 고쳤다.

v1 대비 바뀐 점
  - 봉인 번호(seal_id)가 브랜치 이름과 무관하다. 폴더 이름도 seal_id다(경로 치환 충돌 없음).
  - manifest v2: 머리줄·형식 버전·항목 수, 빈 폴더(D), 파일(F), 경로 규칙 검사, 0개 묶음 표현.
  - 백업은 대조를 마친 봉인본에서 복사한다(작업 폴더에서 다시 복사하지 않음). 복사본은 fsync한다.
  - 어느 단계든 대조에 실패하면 멈추고 참조 파일을 만들지 않는다.
  - 참조값은 Git이 추적하는 참조 파일(.memstore-ref)로 남긴다(PR 본문은 Git에 안 남으므로).
  - 복원은 저장된 참조 파일만 읽고, 백업 위치 ID를 LOCATION.txt 표식으로 찾아 빈 폴더에 복원한다.
    걸린 시간에 대조 시간을 포함한다.
  - 봉인본 쓰기 시도가 막히는지 시험한다(읽기 전용 표시. 보안 장치 아님).

실제 E:·K:는 건드리지 않는다. out_dir 아래에 가상 드라이브 폴더를 만든다.
표준 라이브러리만 쓴다. 아무것도 지우지 않으므로 out_dir은 아직 없는 새 경로여야 한다.

사용: python -I backup_restore_bench_v2.py <out_dir>
"""
import hashlib
import json
import os
import random
import re
import shutil
import stat
import sys
import time
from pathlib import Path

FORMAT = "MEMSTORE-MANIFEST v2"
REF_FORMAT = "MEMSTORE-REF v2"
ROLES = ["pln", "pmo", "rsch"]
WIN_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
BAD_CHARS = re.compile(r'[<>:"|?*\x00-\x1f]')


class SealError(Exception):
    pass


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def new_seal_id():
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + os.urandom(3).hex()


def check_rel_path(rel):
    """경로 규칙: '/' 구분, 절대경로·드라이브·'.'·'..'·제어문자·Windows 금지 문자·예약 이름·끝 점/공백 거부."""
    if not rel or rel.startswith("/") or re.match(r"^[A-Za-z]:", rel) or "\\" in rel:
        raise SealError(f"경로 규칙 위반(절대·드라이브·역슬래시): {rel!r}")
    for part in rel.split("/"):
        if part in ("", ".", "..") or BAD_CHARS.search(part) or part.endswith((".", " ")):
            raise SealError(f"경로 규칙 위반: {rel!r}")
        if part.split(".")[0].upper() in WIN_RESERVED:
            raise SealError(f"Windows 예약 이름: {rel!r}")


def scan(root):
    """(종류, 상대경로) 목록. 심볼릭 링크·junction(재분석 지점)이 있으면 봉인을 멈춘다."""
    entries = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for name in dirnames + filenames:
            p = Path(dirpath) / name
            st = os.lstat(p)
            if stat.S_ISLNK(st.st_mode) or (getattr(st, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
                raise SealError(f"링크·재분석 지점은 봉인하지 않음: {p.relative_to(root).as_posix()}")
        rel_dir = Path(dirpath).relative_to(root).as_posix()
        if rel_dir != "." and not dirnames and not filenames:
            entries.append(("D", rel_dir))
        for name in filenames:
            entries.append(("F", (Path(dirpath) / name).relative_to(root).as_posix()))
    seen = {}
    for kind, rel in entries:
        check_rel_path(rel)
        key = rel.casefold()
        if key in seen:
            raise SealError(f"대소문자만 다른 이름 충돌: {seen[key]!r} / {rel!r}")
        seen[key] = rel
    return sorted(entries, key=lambda e: e[1].encode("utf-8"))


def build_manifest(root, seal_id, bundle_id):
    lines = [FORMAT, f"seal_id\t{seal_id}", f"bundle_id\t{bundle_id}"]
    body = []
    for kind, rel in scan(root):
        if kind == "D":
            body.append(f"D\t{rel}")
        else:
            p = root / rel
            body.append(f"F\t{rel}\t{p.stat().st_size}\t{sha256_file(p)}")
    lines.append(f"entries\t{len(body)}")
    text = "\n".join(lines + body) + "\n"
    return text.encode("utf-8")


def parse_manifest(raw):
    text = raw.decode("utf-8")
    if text.startswith("﻿") or not text.endswith("\n"):
        raise SealError("manifest 형식: BOM 또는 끝 줄바꿈 없음")
    lines = text[:-1].split("\n")
    if lines[0] != FORMAT:
        raise SealError("manifest 형식 버전 다름")
    head = dict(ln.split("\t", 1) for ln in lines[1:4])
    entries = {}
    for ln in lines[4:]:
        parts = ln.split("\t")
        check_rel_path(parts[1])
        if parts[1] in entries:
            raise SealError(f"manifest 중복 경로: {parts[1]}")
        entries[parts[1]] = parts
    if int(head["entries"]) != len(entries):
        raise SealError("manifest 항목 수 불일치")
    return head, entries


def verify_tree(root, manifest_raw, expected_sha):
    """문제 목록을 돌려준다(빈 목록 = 완전 일치). manifest 지문과 문법을 먼저 본다."""
    if hashlib.sha256(manifest_raw).hexdigest() != expected_sha:
        return ["manifest 지문 불일치"]
    try:
        _, entries = parse_manifest(manifest_raw)
    except SealError as e:
        return [f"manifest 문법: {e}"]
    problems = []
    actual = {}
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root).as_posix()
        if rel_dir != "." and not dirnames and not filenames:
            actual[rel_dir] = "D"
        for n in filenames:
            actual[(Path(dirpath) / n).relative_to(root).as_posix()] = "F"
    for rel, parts in entries.items():
        if rel not in actual:
            problems.append(f"누락: {rel}")
        elif parts[0] == "F":
            p = root / rel
            if p.stat().st_size != int(parts[2]):
                problems.append(f"크기 다름: {rel}")
            elif sha256_file(p) != parts[3]:
                problems.append(f"내용 다름: {rel}")
    for rel in sorted(set(actual) - set(entries)):
        problems.append(f"목록에 없는 항목: {rel}")
    return problems


def copy_tree_durable(src, dst):
    # 읽기 전용 속성은 복사하지 않는다(fsync에 쓰기 핸들이 필요). 대조 뒤에 다시 읽기 전용으로 표시한다.
    shutil.copytree(src, dst, copy_function=shutil.copyfile)
    for p in dst.rglob("*"):
        if p.is_file():
            with open(p, "rb+") as f:
                os.fsync(f.fileno())


def set_readonly(root):
    for p in root.rglob("*"):
        if p.is_file():
            os.chmod(p, stat.S_IREAD)


def make_location(root, loc_id):
    (root / "MEMSTORE_BACKUP").mkdir(parents=True)
    (root / "MEMSTORE_BACKUP" / "LOCATION.txt").write_text(f"location_id: {loc_id}\n", encoding="utf-8")
    return root / "MEMSTORE_BACKUP"


def find_location(drive_roots, loc_id):
    for d in drive_roots:
        marker = d / "MEMSTORE_BACKUP" / "LOCATION.txt"
        if marker.exists() and f"location_id: {loc_id}" in marker.read_text(encoding="utf-8"):
            return d / "MEMSTORE_BACKUP"
    raise SealError(f"백업 위치를 찾지 못함: {loc_id}")


def seal_and_backup(work, archive_root, backups, refs_dir, store_id, bundle_id, source_commit,
                    corrupt_after_copy=None):
    """봉인 → 봉인본 대조 → 백업마다 복사·대조 → (모두 통과하면) 참조 파일. 실패하면 SealError."""
    seal_id = new_seal_id()
    manifest = build_manifest(work, seal_id, bundle_id)
    msha = hashlib.sha256(manifest).hexdigest()
    seal_dir = archive_root / store_id / "seals" / seal_id
    seal_dir.mkdir(parents=True)
    (seal_dir / "MANIFEST.tsv").write_bytes(manifest)
    copy_tree_durable(work, seal_dir / "bundle")
    probs = verify_tree(seal_dir / "bundle", manifest, msha)
    if probs:
        raise SealError(f"봉인본 대조 실패: {probs}")
    set_readonly(seal_dir)
    done = []
    for loc_id, loc_root in backups:
        dst = loc_root / store_id / "seals" / seal_id
        dst.mkdir(parents=True)
        shutil.copyfile(seal_dir / "MANIFEST.tsv", dst / "MANIFEST.tsv")
        copy_tree_durable(seal_dir / "bundle", dst / "bundle")  # 대조를 마친 봉인본에서 복사
        if corrupt_after_copy == loc_id:
            victim = next(p for p in (dst / "bundle").rglob("*") if p.is_file())
            os.chmod(victim, stat.S_IREAD | stat.S_IWRITE)
            victim.write_bytes(victim.read_bytes() + b"x")
        probs = verify_tree(dst / "bundle", (dst / "MANIFEST.tsv").read_bytes(), msha)
        if probs:
            raise SealError(f"백업 {loc_id} 대조 실패, 참조 파일을 만들지 않음: {probs}")
        set_readonly(dst)
        done.append(loc_id)
    files = sum(1 for _ in (seal_dir / "bundle").rglob("*") if _.is_file())
    ref = {"format": REF_FORMAT, "store_id": store_id, "seal_id": seal_id, "bundle_id": bundle_id,
           "source_commit": source_commit, "sealed_at_utc": seal_id.split("-")[0], "device_id": "HANAL",
           "roles": ",".join(sorted(p.name for p in work.iterdir() if p.is_dir())),
           "files": files, "manifest_sha256": msha, "backups": ",".join(done)}
    ref_path = refs_dir / f"{seal_id}.memstore-ref"
    ref_path.write_text("".join(f"{k}: {v}\n" for k, v in ref.items()), encoding="utf-8", newline="\n")
    return ref_path


def read_ref(path):
    return dict(ln.split(": ", 1) for ln in path.read_text(encoding="utf-8").splitlines())


def restore(ref_path, drive_roots, dest, prefer=None):
    """참조 파일만 보고 복원한다. 걸린 시간에는 대조가 포함된다."""
    t = time.perf_counter()
    ref = read_ref(ref_path)
    loc_ids = [prefer] if prefer else ref["backups"].split(",")
    last = None
    for loc_id in loc_ids:
        try:
            loc = find_location(drive_roots, loc_id)
        except SealError as e:
            last = str(e)
            continue
        src = loc / ref["store_id"] / "seals" / ref["seal_id"]
        manifest = (src / "MANIFEST.tsv").read_bytes()
        if hashlib.sha256(manifest).hexdigest() != ref["manifest_sha256"]:
            last = f"{loc_id}: manifest 지문 불일치"
            continue
        shutil.copytree(src / "bundle", dest)
        probs = verify_tree(dest, manifest, ref["manifest_sha256"])
        return {"location": loc_id, "problems": probs, "seconds_incl_verify": time.perf_counter() - t}
    return {"location": None, "problems": [last], "seconds_incl_verify": time.perf_counter() - t}


def make_bundle(work, seed=7):
    rnd = random.Random(seed)
    for r in ROLES:
        d = work / r
        (d / "test-data").mkdir(parents=True)
        with open(d / "memo.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for i in range(200):
                f.write(json.dumps({"role": r, "seq": i + 1, "now": f"작업 {i}"}, ensure_ascii=False) + "\n")
        (d / "노트.md").write_bytes(f"# {r} 노트\r\n- 원본 줄바꿈 CRLF 그대로\r\n".encode("utf-8"))
        for k in range(5):
            (d / "test-data" / f"sample_{k}.bin").write_bytes(rnd.randbytes(20_000))
    (work / "rsch" / "empty-dir").mkdir()


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=False)
    drive_e, drive_k = out / "drive_E", out / "drive_K"
    loc_e, loc_k = make_location(drive_e, "hdd-e-primary"), make_location(drive_k, "hdd-k-secondary")
    archive = out / "store" / "archive"
    refs = out / "domain_git" / "memstore-refs"
    refs.mkdir(parents=True)
    store_id, commit = "memstore-01", "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
    backups = [("hdd-e-primary", loc_e), ("hdd-k-secondary", loc_k)]
    results = {}

    work = out / "store" / "work" / "feat-f3"
    make_bundle(work)
    t = time.perf_counter()
    ref_path = seal_and_backup(work, archive, backups, refs, store_id, "rhs/order/feat-f3", commit)
    results["seal_and_backup_seconds"] = time.perf_counter() - t
    results["reference_file"] = ref_path.read_text(encoding="utf-8")
    roots = [drive_e, drive_k]
    results["restore_from_E"] = restore(ref_path, roots, out / "restore_E", prefer="hdd-e-primary")
    results["restore_from_K"] = restore(ref_path, roots, out / "restore_K", prefer="hdd-k-secondary")

    faults = {}
    # 1) 봉인본에 쓰기 시도 → 막혀야 함
    sealed_file = next((archive / store_id / "seals").rglob("memo.jsonl"))
    try:
        with open(sealed_file, "a", encoding="utf-8") as f:
            f.write("tamper\n")
        faults["write_to_sealed_blocked"] = False
    except PermissionError:
        faults["write_to_sealed_blocked"] = True
    # 2) 백업 대조 실패 → 봉인이 멈추고 참조 파일이 생기지 않아야 함
    work2 = out / "store" / "work" / "feat-f4"
    make_bundle(work2, seed=8)
    before = set(refs.iterdir())
    try:
        seal_and_backup(work2, archive, backups, refs, store_id, "rhs/order/feat-f4", commit,
                        corrupt_after_copy="hdd-k-secondary")
        faults["stop_on_backup_mismatch"] = {"stopped": False}
    except SealError as e:
        faults["stop_on_backup_mismatch"] = {"stopped": True, "ref_created": set(refs.iterdir()) != before,
                                             "reason": str(e)[:120]}
    # 3) E: 백업 1바이트 손상 → E에서 복원하면 잡히고, K에서는 정상 복원
    seal_id = read_ref(ref_path)["seal_id"]
    victim = next((loc_e / store_id / "seals" / seal_id / "bundle").rglob("sample_2.bin"))
    os.chmod(victim, stat.S_IREAD | stat.S_IWRITE)
    b = bytearray(victim.read_bytes())
    b[100] ^= 1
    victim.write_bytes(bytes(b))
    faults["corrupt_E_restore_E"] = restore(ref_path, roots, out / "restore_E_corrupt", prefer="hdd-e-primary")["problems"]
    faults["corrupt_E_restore_K"] = restore(ref_path, roots, out / "restore_K_after", prefer="hdd-k-secondary")["problems"]
    # 4) 드라이브 문자가 바뀌어도 표식으로 찾는지 (다른 위치 목록 순서)
    faults["find_by_marker_any_order"] = str(find_location([drive_k, drive_e], "hdd-e-primary")) == str(loc_e)
    # 5) 경로 규칙 위반 → 봉인 거부
    work3 = out / "store" / "work" / "bad-names"
    (work3 / "pln").mkdir(parents=True)
    (work3 / "pln" / "ok.txt").write_text("x", encoding="utf-8")
    (work3 / "pln" / "trailing.").mkdir() if os.name != "nt" else None
    (work3 / "pln" / "AUX.txt.md").write_text("x", encoding="utf-8")  # 예약 이름 'AUX'
    try:
        build_manifest(work3, "test", "x")
        faults["reserved_name_rejected"] = False
    except SealError as e:
        faults["reserved_name_rejected"] = str(e)
    # 6) 빈 묶음 → manifest가 entries 0으로 표현되고 대조 통과
    work4 = out / "store" / "work" / "empty"
    work4.mkdir(parents=True)
    m = build_manifest(work4, "test", "empty")
    faults["empty_bundle_manifest"] = {"text": m.decode("utf-8"),
                                       "verify": verify_tree(work4, m, hashlib.sha256(m).hexdigest())}
    # 7) manifest 중복 경로 → 거부
    dup = (FORMAT + "\nseal_id\tx\nbundle_id\tx\nentries\t2\nF\ta.txt\t1\t" + "0" * 64 + "\nF\ta.txt\t1\t" + "0" * 64 + "\n").encode()
    faults["duplicate_path_rejected"] = verify_tree(work4, dup, hashlib.sha256(dup).hexdigest())
    # 8) 원본 줄바꿈(CRLF) 보존
    restored_note = (out / "restore_K" / "pln" / "노트.md").read_bytes()
    faults["original_crlf_preserved"] = b"\r\n" in restored_note
    results["faults"] = faults
    (out / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
