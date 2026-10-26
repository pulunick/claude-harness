#!/usr/bin/env python3
"""각자 기기에서 한 번 — (1) 커밋에 찍힐 신원(harness.who / harness.machine) 설정, (2) Claude 메모리 폴더를 저장소에 연결.

    python setup/common/link_memory.py --who 하늘 --machine mac
    python setup/common/link_memory.py                      # 인자 없으면 물어본다
    python setup/common/link_memory.py --status             # 확인만

왜: Claude Code는 ~/.claude/projects/<경로인코딩>/memory/ 를 세션마다 자동 로드하는데 이건 기기 로컬이다.
    그 폴더를 저장소의 .claude/memory 로 링크(맥 심링크 / 윈도우 정션)하면 Claude가 쓰는 메모리가 곧 커밋 대상이 되어
    두 사람이 공유된다. 경로인코딩 = 저장소 절대경로의 영숫자 아닌 문자를 전부 '-' 로 (PINE 하네스 SETUP §3-7 과 같은 규칙).
주의: 세션은 반드시 저장소 루트에서 연다 — 하위 폴더에서 열면 다른 인코딩 폴더를 본다.
"""
import argparse
import datetime as dt
import os
import pathlib
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parents[2]
TARGET = ROOT / ".claude" / "memory"
ENC = re.sub(r"[^A-Za-z0-9]", "-", str(ROOT))
LINK = pathlib.Path.home() / ".claude" / "projects" / ENC / "memory"
IS_WIN = os.name == "nt"


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout.strip()


def linked():
    try:
        return LINK.exists() and LINK.resolve() == TARGET.resolve()
    except Exception:
        return False


def status():
    print(f"저장소: {ROOT}")
    print(f"신원: who={git('config', 'harness.who') or '(없음)'} machine={git('config', 'harness.machine') or '(없음)'} user.name={git('config', 'user.name') or '(없음)'}")
    print(f"메모리 링크: {LINK}")
    print("  → " + ("저장소 .claude/memory 에 연결됨 ✅" if linked() else ("다른 곳을 가리킴/일반 폴더 ⚠" if LINK.exists() else "없음")))


def set_identity(who, machine):
    if not who:
        who = input("커밋에 찍힐 이름 (예: 하늘): ").strip()
    if not machine:
        default = "win" if IS_WIN else "mac"
        machine = input(f"기기 이름 [{default}]: ").strip() or default
    git("config", "harness.who", who)
    git("config", "harness.machine", machine)
    if not git("config", "user.name"):
        git("config", "user.name", who)
    # git 쪽 물리 장치: 트레일러 자동 부착·금지 파일 차단 훅, pull 은 항상 rebase
    git("config", "core.hooksPath", ".githooks")
    git("config", "pull.rebase", "true")
    git("config", "rebase.autoStash", "true")
    if not IS_WIN:
        for h in (ROOT / ".githooks").glob("*"):
            h.chmod(0o755)
    print(f"신원 설정: Worked-by: {who}@{machine}  (이 저장소의 .git/config 에만 저장)")
    print("git 설정: core.hooksPath=.githooks (트레일러 자동·금지 파일 차단) · pull.rebase=true · rebase.autoStash=true")


def link():
    TARGET.mkdir(parents=True, exist_ok=True)
    LINK.parent.mkdir(parents=True, exist_ok=True)
    if linked():
        print("메모리 링크: 이미 연결됨 ✅")
        return
    if LINK.exists() or LINK.is_symlink():
        bak = LINK.with_name(f"memory.bak-{dt.date.today():%Y%m%d}")
        LINK.rename(bak)
        print(f"기존 메모리 폴더를 백업: {bak}\n  → 안에 쓸 만한 메모리가 있으면 .claude/memory 로 손으로 옮기고 MEMORY.md 색인에 추가 (자동 병합 안 함)")
    if IS_WIN:
        r = subprocess.run(["cmd", "/c", "mklink", "/J", str(LINK), str(TARGET)], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"정션 생성 실패: {r.stderr or r.stdout}")
    else:
        os.symlink(TARGET, LINK)
    print(f"메모리 링크 생성: {LINK} → {TARGET}" + ("" if linked() else "  ⚠ 확인 실패 — --status 로 다시 확인"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--who")
    ap.add_argument("--machine")
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    if a.status:
        status()
        sys.exit(0)
    set_identity(a.who, a.machine)
    link()
    print("\n다음: 저장소 루트에서 claude 실행 → 세션 시작 훅 출력에 '메모리: … 연결됨' 이 보이면 끝")
