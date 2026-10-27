#!/usr/bin/env python3
"""새 프로젝트 초기화 — 템플릿의 자리표시자를 채운다. 표준 라이브러리만.

    python3 setup/init.py                                   # 인자 없으면 물어본다
    python3 setup/init.py --project my-app --title "내 앱" --owner me \
        --members 하늘:mac,바다:win,산:mac [--with craft,film] [--labels]
    # 첫 멤버 = 나(저장소를 만든 사람). 2명이든 5명이든 같다. (--person-a/--person-b 옛 인자도 받는다)

하는 일:
  1. 저장소 안 텍스트 파일의 {{PROJECT}} {{PROJECT_TITLE}} {{OWNER}} {{REPO}} {{DESCRIPTION}} {{DATE}}
     {{MEMBERS}}(이름(기기) 목록) {{MEMBER_TAGS}}(`[이름]`/…/`[누구나]`) {{PERSON_A}} {{MACHINE_A}}(첫 멤버 = 나)
     {{PERSON_B}} {{MACHINE_B}}(두 번째 멤버 — 부트스트랩 프롬프트 기본값, 다른 멤버는 이름만 바꿔 보낸다) 를 치환
  2. README.project.md → README.md (하네스 설명 README 를 프로젝트 README 로 교체)
  3. --with <모듈,…> : optional/<모듈>/ 을 켠다 (표·설정은 setup/modules.py). 그리고 .claude/harness.json 을 써서
     이후 하네스 변경을 setup/sync.py 로 받을 수 있게 한다 (--with-craft 는 --with craft 와 같다)
  4. --labels     : /issue 용 라벨 6종을 gh 로 생성 (없으면 명령만 출력)
한 번만 실행한다. 자리표시자가 더 없으면 (이미 초기화됨) 치환 단계는 건너뛴다.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_EXT = {".md", ".py", ".sh", ".ps1", ".json", ".txt", ".yml", ".yaml", ".toml", ".gitignore", ".gitattributes", ""}
SKIP_DIRS = {".git", "optional", "node_modules", "__pycache__"}
SKIP_FILES = {"setup/init.py", "README.md"}  # 하네스 README 는 2단계에서 통째로 교체
LABELS = [("버그", "d73a4a"), ("환경", "fbca04"), ("결정", "d876e3"), ("도움", "008672"), ("검토", "0075ca"), ("아이디어", "a2eeef")]


def ask(prompt, default=None):
    s = input(f"{prompt}" + (f" [{default}]" if default else "") + ": ").strip()
    return s or default or ""


def text_files():
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts) or str(rel) in SKIP_FILES:
            continue
        if p.suffix in TEXT_EXT or p.name.startswith("."):
            yield p


def substitute(values):
    pat = re.compile(r"\{\{(" + "|".join(values) + r")\}\}")
    changed = 0
    for p in text_files():
        try:
            raw = p.read_bytes()
        except OSError:
            continue
        bom = raw.startswith(b"\xef\xbb\xbf")
        try:
            s = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            continue
        new = pat.sub(lambda m: values[m.group(1)], s)
        if new != s:
            p.write_bytes((b"\xef\xbb\xbf" if bom else b"") + new.encode("utf-8"))
            changed += 1
    return changed


def remaining_placeholders():
    found = set()
    for p in text_files():
        try:
            s = p.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        found.update(re.findall(r"\{\{([A-Z_]+)\}\}", s))
    return found


def enable_modules(mods):
    """optional 모듈을 켠다 — 표와 한 번만 하는 설정은 setup/modules.py, 공용 파일은 거기 목록대로 복사. 그리고 manifest."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import modules as M
    sync_py = Path(__file__).resolve().parent / "sync.py"
    all_mods = list(dict.fromkeys(M.PROFILE_DEFAULTS["team"] + mods))
    for mod in mods:
        if mod not in M.MODULES:
            print(f"[모듈] 모르는 모듈 {mod} — 가능: {list(M.MODULES)}")
            continue
        for n in M.enable(mod, ROOT, "team", all_mods):
            print(f"[{mod}] {n}")
        for src, dst in M.files_of(mod, "team"):
            d = ROOT / dst
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(M.HARNESS / src, d)
        if mod == "craft":
            for d in ("craft/vector", "craft/photo", "craft/effect", "craft/design", "craft/film", "craft/sound", "craft/out"):
                (ROOT / d / ".gitkeep").touch()
            print("[craft] 설치 스크립트·프로젝트 스킬·CLAUDE.md 절·MCP 허용 목록 추가됨. 각 기기에서 setup/<os>/install-craft.* 실행")
    # 이 저장소가 템플릿의 사본이면(ROOT ≠ HARNESS) manifest 를 써서 sync.py 로 공용 파일을 받을 수 있게 한다
    if ROOT.resolve() != M.HARNESS.resolve():
        commit = subprocess.run(["git", "-C", str(M.HARNESS), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        M.write_manifest(ROOT, "team", all_mods, commit)
        M.merge_settings(ROOT, {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": M.CHECK_HOOK}]}]}})
        M.register(ROOT)
        print(f"[하네스] .claude/harness.json ({', '.join(all_mods)}) — 공용 파일 갱신은 python3 {sync_py} {ROOT}")


def create_labels(do_it):
    cmds = [f'gh label create "{n}" --color {c} --force' for n, c in LABELS]
    if do_it and shutil.which("gh"):
        for cmd in cmds:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            print(("[label] " if r.returncode == 0 else "[label 실패] ") + cmd.split('"')[1] + ("" if r.returncode == 0 else " — " + r.stderr.strip()[:80]))
    else:
        print("[label] /issue 용 라벨은 저장소에 한 번 만들어야 한다 (gh 로그인 후):")
        for cmd in cmds:
            print("   " + cmd)


def parse_members(a):
    """--members '하늘:mac,바다:win' → [(이름, 기기), …]. 없으면 --person-a/b, 그것도 없으면 물어본다(빈 줄이면 끝)."""
    if a.members:
        out = []
        for tok in a.members.split(","):
            name, _, mach = tok.strip().partition(":")
            out.append((name, mach or "mac"))
        return out
    if a.person_a:
        out = [(a.person_a, a.machine_a or "mac")]
        if a.person_b:
            out.append((a.person_b, a.machine_b or "win"))
        return out
    out = []
    print("멤버를 한 명씩 입력한다. 첫 번째가 나. 이름을 비우면 끝.")
    while True:
        name = ask(f"멤버 {len(out) + 1} 이름" + (" (나)" if not out else ""))
        if not name:
            break
        mach = ask("  기기 (mac|win|…)", "mac" if (not out and sys.platform == "darwin") else "win")
        out.append((name, mach))
    if not out:
        sys.exit("멤버가 없다 — --members 로 지정")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", help="저장소 이름(슬러그)")
    ap.add_argument("--title", help="프로젝트 한글 제목 (CLAUDE.md 제목)")
    ap.add_argument("--owner", help="GitHub 소유자(사용자/조직)")
    ap.add_argument("--description", default="", help="한 줄 설명")
    ap.add_argument("--members", help="멤버 목록 '이름:기기,이름:기기,…' — 첫 멤버가 나")
    ap.add_argument("--person-a", help="(구식) 나 이름 — --members 가 없을 때")
    ap.add_argument("--machine-a", help="내 기기 (mac|win|…)")
    ap.add_argument("--person-b", help="상대 이름")
    ap.add_argument("--machine-b", help="상대 기기 (mac|win|…)")
    ap.add_argument("--with", dest="with_mods", default="", help="optional 모듈 목록, 쉼표 구분: craft,film")
    ap.add_argument("--with-craft", action="store_true", help="(= --with craft)")
    ap.add_argument("--labels", action="store_true", help="gh 로 이슈 라벨 생성")
    a = ap.parse_args()

    left = remaining_placeholders()
    if left:
        repo_dir = ROOT.name
        project = a.project or ask("저장소 이름(슬러그)", repo_dir)
        title = a.title or ask("프로젝트 제목(한글)", project)
        owner = a.owner or ask("GitHub 소유자(owner)")
        desc = a.description or ask("한 줄 설명", title)
        members = parse_members(a)
        person_a, machine_a = members[0]
        person_b, machine_b = members[1] if len(members) > 1 else ("<상대>", "win")
        values = {
            "MEMBERS": "·".join(f"{n}({m})" for n, m in members),
            "MEMBER_TAGS": "/".join(f"`[{n}]`" for n, _ in members) + "/`[누구나]`",
            "PROJECT": project, "PROJECT_TITLE": title, "OWNER": owner, "REPO": f"{owner}/{project}",
            "DESCRIPTION": desc, "PERSON_A": person_a, "MACHINE_A": machine_a,
            "PERSON_B": person_b, "MACHINE_B": machine_b, "DATE": datetime.date.today().isoformat(),
        }
        n = substitute(values)
        print(f"[init] 자리표시자 치환: 파일 {n}개")
        proj_readme = ROOT / "README.project.md"
        if proj_readme.exists():
            proj_readme.replace(ROOT / "README.md")
            print("[init] README.md 를 프로젝트용으로 교체")
        still = remaining_placeholders()
        if still:
            print(f"[init] ⚠ 남은 자리표시자: {sorted(still)}")
    else:
        print("[init] 자리표시자 없음 — 이미 초기화된 저장소. 치환 단계 건너뜀")

    mods = [m for m in a.with_mods.split(",") if m] + (["craft"] if a.with_craft else [])
    enable_modules(list(dict.fromkeys(mods)))
    create_labels(a.labels)

    print("\n다음:")
    print("  1. python3 setup/common/link_memory.py --who <내 이름> --machine <기기>   # 신원·메모리 링크·git 훅")
    print("  2. python3 tools/harness/doctor.py                                      # FAIL 0 확인")
    print("  3. git add <파일 나열> && git commit -m '하네스: 템플릿 초기화' && git push")
    print("  4. 상대에게 setup/windows/bootstrap-prompt.md 의 회색 박스를 보낸다 (맥이면 setup/README.md 맥 절)")
    print("  5. claude → /start")


if __name__ == "__main__":
    os.chdir(ROOT)
    main()
