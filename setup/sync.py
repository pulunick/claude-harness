#!/usr/bin/env python3
"""하네스 공용 파일을 프로젝트에 입히고(init) 갱신하고(sync) 뒤처짐을 알린다(check). 표준 라이브러리만.

    python3 setup/sync.py init <프로젝트> --profile solo [--with craft,film|post] [--title "제목"] [--desc "한 줄"] [--bare]
        새 폴더든 기존 프로젝트든 하네스를 입힌다. 프로젝트 소유 파일(CLAUDE.md·BRAIN·STATE·settings)은 없을 때만 만들고,
        공용 파일은 복사하고, .claude/harness.json 을 쓰고, ~/.claude/harness-projects.txt 에 등록한다.
        --bare: 이미 돌아가는 프로젝트에 입힐 때 — CLAUDE.md 절 추가·폴더 생성 같은 enable 은 생략.
        team 프로필은 `gh repo create --template` + setup/init.py 경로를 쓴다(이 명령은 manifest 만 보강).
    python3 setup/sync.py <프로젝트> [--dry-run] [--force]       공용 파일 갱신 (3-way: 프로젝트가 손댄 파일은 충돌로 보고만)
    python3 setup/sync.py --all [--dry-run]                      등록된 프로젝트 전부
    python3 setup/sync.py --check <프로젝트>                      SessionStart 훅용 한 줄 — 뒤처졌을 때만 출력, 아니면 침묵
    python3 setup/sync.py --list                                 등록된 프로젝트와 상태

규칙: 하네스에 커밋 안 된 변경이 있으면 sync 는 멈춘다(manifest 의 commit 이 실제 복사본과 어긋나지 않게).
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import modules as M  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def git(*args, timeout=10):
    try:
        r = subprocess.run(["git", "-C", str(M.HARNESS), *args], capture_output=True, timeout=timeout)
        return r.returncode, r.stdout
    except Exception:
        return 1, b""


def head():
    rc, out = git("rev-parse", "HEAD")
    return out.decode().strip() if rc == 0 else ""


def show(commit, rel):
    rc, out = git("show", f"{commit}:{rel}")
    return out if rc == 0 else None


def dirty():
    rc, out = git("status", "--porcelain")
    return bool(out.strip())


def sync_project(root, dry=False, force=False, quiet=False):
    root = Path(root).resolve()
    m = M.read_manifest(root)
    if not m:
        print(f"{root}: .claude/harness.json 없음 → sync.py init 먼저")
        return 1
    profile, mods, base_commit = m["profile"], m["modules"], m.get("commit") or ""
    cur = head()
    added, updated, conflicts, same = [], [], [], 0
    for src, dst in M.all_files(mods, profile):
        s_path = M.HARNESS / src
        if not s_path.exists():
            continue
        s = s_path.read_bytes()
        d = root / dst
        if d.exists() and d.read_bytes() == s:
            same += 1
            continue
        base = show(base_commit, src) if base_commit else None
        if not d.exists():
            added.append(dst)
        elif force or (base is not None and d.read_bytes() == base):
            updated.append(dst)
        else:
            conflicts.append(dst)
            continue
        if not dry:
            d.parent.mkdir(parents=True, exist_ok=True)
            d.write_bytes(s)
            if s_path.stat().st_mode & 0o111:
                d.chmod(d.stat().st_mode | 0o111)
    # 프로젝트 소유 파일에 합쳐진 조각이 바뀌었으면 손으로 볼 것
    changed_snips = []
    if base_commit and base_commit != cur:
        for sn in M.snippets_of(mods):
            rc, out = git("diff", "--quiet", base_commit, cur, "--", sn)
            if rc == 1:
                changed_snips.append(sn)
    if not dry and not conflicts:
        M.write_manifest(root, profile, mods, cur)
    if quiet and not (added or updated or conflicts or changed_snips):
        return 0
    tag = "(dry-run) " if dry else ""
    print(f"{tag}{root.name} [{profile}: {','.join(mods)}] 동일 {same}" +
          (f" · 추가 {len(added)}" if added else "") + (f" · 갱신 {len(updated)}" if updated else "") +
          (f" · ⚠ 충돌 {len(conflicts)}" if conflicts else ""))
    for f in added:
        print(f"  + {f}")
    for f in updated:
        print(f"  ↻ {f}")
    for f in conflicts:
        print(f"  ⚠ {f} — 프로젝트에서 손댄 공용 파일. 하네스로 되가져가거나 --force 로 덮어쓴다")
    for sn in changed_snips:
        print(f"  ✎ {sn} 이 바뀜 — 프로젝트 소유 파일(CLAUDE.md/settings.json/.mcp.json)에 손으로 반영할지 확인")
    if conflicts and not dry:
        print("  충돌이 있어 manifest 의 commit 은 그대로 둔다")
    return 2 if conflicts else 0


def check(root):
    """훅용: 뒤처졌을 때만 한 줄. 어떤 오류도 삼킨다."""
    try:
        root = Path(root).resolve()
        m = M.read_manifest(root)
        if not m or not m.get("commit"):
            return
        cur = head()
        if not cur or cur == m["commit"]:
            return
        paths = [src for src, _ in M.all_files(m["modules"], m["profile"])] + M.snippets_of(m["modules"])
        rc, out = git("rev-list", "--count", f"{m['commit']}..{cur}", "--", *paths)
        n = int(out.decode().strip() or 0) if rc == 0 else 0
        if n:
            rc, names = git("diff", "--name-only", m["commit"], cur, "--", *paths)
            files = [l for l in names.decode().splitlines() if l.strip()]
            print(f"[하네스] 템플릿보다 {n}커밋 뒤 ({len(files)}파일: {', '.join(Path(f).name for f in files[:4])}"
                  f"{' …' if len(files) > 4 else ''}) → python3 {M.HARNESS}/setup/sync.py {root}")
    except Exception:
        return


def init(root, profile, with_mods, title, desc, bare=False):
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    mods = list(dict.fromkeys(M.PROFILE_DEFAULTS[profile] + with_mods))
    existing = M.read_manifest(root)
    if existing:
        mods = list(dict.fromkeys(existing["modules"] + mods))
    notes = []
    if profile == "team" and not (root / ".claude" / "commands" / "start.md").exists():
        print(f"team 프로필의 새 프로젝트는 `gh repo create --template {M.harness_url().replace('https://github.com/', '')}` 후 `setup/init.py` 로 만든다. "
              "여기서는 기존 team 저장소에 manifest 만 입힌다.")
    for mod in mods:
        if bare or mod in ("core", "team"):
            continue
        notes += M.enable(mod, root, profile, mods)
    if profile == "solo":
        import datetime
        made = M.install_profile(root, "solo", {"PROJECT_TITLE": title or root.name, "DESCRIPTION": desc or "",
                                                 "DATE": datetime.date.today().isoformat(),
                                                 # film/ 아래 채널만 브리지 포트를 배정표에 적는다 (밖이면 headless .mcp.json 이라 할 일 없음)
                                                 "FILM_PORT_TASK": "- [ ] `.mcp.json`의 `<film포트>`·`<effect포트>`를 `../README.md` 배정표에 적고 채우기\n"
                                                 if M.film_parent(root) else ""}, mods)
        notes += [f"만듦: {f}" for f in made]
    else:
        M.merge_settings(root, {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": M.CHECK_HOOK}]}]}})
    M.write_manifest(root, profile, mods, existing["commit"] if existing and existing.get("commit") else "")
    M.register(root)
    print(f"{root.name}: 프로필 {profile}, 모듈 {','.join(mods)} — 등록됨 ({M.REGISTRY})")
    for n in notes:
        print("  · " + n)
    # 공용 파일: 없는 건 추가, 이미 있는데 다르면 충돌로 보고 (기존 프로젝트를 입힐 때 고친 흔적을 지우지 않게) → 보고 --force
    return sync_project(root)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", nargs="*")
    ap.add_argument("--profile", choices=["solo", "team"], default="solo")
    ap.add_argument("--with", dest="with_mods", default="", help="모듈 목록 쉼표 구분: craft,film,post,mockup (film·post 는 택1)")
    ap.add_argument("--title"); ap.add_argument("--desc")
    ap.add_argument("--bare", action="store_true", help="init: 기존 프로젝트에 manifest·점검 훅·공용 파일만 (CLAUDE.md 절·폴더 등 enable 생략)")
    ap.add_argument("--all", action="store_true"); ap.add_argument("--list", action="store_true")
    ap.add_argument("--check", metavar="PROJECT")
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--force", action="store_true")
    ap.add_argument("--allow-dirty", action="store_true", help="하네스에 커밋 안 된 변경이 있어도 진행(검증용)")
    a = ap.parse_args()

    if a.check:
        return check(a.check)
    if a.list:
        for p in M.registered():
            m = M.read_manifest(p) or {}
            print(f"{p}  [{m.get('profile','?')}: {','.join(m.get('modules', []))}]  {m.get('commit','')[:7]} {m.get('synced','')}")
        return 0
    if not a.allow_dirty and dirty():
        sys.exit("하네스에 커밋 안 된 변경이 있다 — 먼저 커밋하고 sync (manifest 의 commit 과 복사본이 어긋나지 않게). 검증만이면 --allow-dirty")
    if a.target and a.target[0] == "init":
        if len(a.target) < 2:
            sys.exit("init <프로젝트 경로>")
        mods = [x for x in a.with_mods.split(",") if x]
        bad = [x for x in mods if x not in M.MODULES]
        if bad:
            sys.exit(f"모르는 모듈: {bad} (가능: {list(M.MODULES)})")
        if "film" in mods and "post" in mods:
            sys.exit("film 과 post 는 같이 켜지 않는다 — 유튜브 회차형은 film, SNS 게시물형은 post")
        return init(a.target[1], a.profile, mods, a.title, a.desc, bare=a.bare)
    targets = M.registered() if a.all else a.target
    if not targets:
        ap.print_help()
        return 1
    rc = 0
    for t in targets:
        rc = max(rc, sync_project(t, dry=a.dry_run, force=a.force, quiet=a.all))
    return rc


if __name__ == "__main__":
    sys.exit(main() or 0)
