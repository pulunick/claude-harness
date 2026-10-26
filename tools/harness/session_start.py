#!/usr/bin/env python3
"""세션 시작 훅 — 누가 어디서 마지막으로 무엇을 했는지, 내가 원격보다 뒤처졌는지, 다음 작업이 무엇인지 한눈에.

출력은 Claude 컨텍스트에 그대로 들어간다(SessionStart 훅 stdout). 사람이 `python tools/harness/session_start.py`로
직접 돌려도 된다. 표준 라이브러리만. 어떤 오류에서도 세션을 막지 않는다(fail-open).
"""
import os
import pathlib
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or pathlib.Path(__file__).resolve().parents[2])


def git(*args, timeout=10):
    try:
        r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""


def main():
    out = []
    who = git("config", "harness.who") or git("config", "user.name") or "(미설정)"
    machine = git("config", "harness.machine") or {"darwin": "mac", "win32": "win"}.get(sys.platform, sys.platform)
    out.append(f"[하네스] 나 = {who}@{machine}" + ("  ⚠ 신원 미설정 → python setup/common/link_memory.py" if who == "(미설정)" else ""))

    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "?"
    fetched = True
    try:
        subprocess.run(["git", "-C", str(ROOT), "fetch", "-q", "--no-tags"], capture_output=True, timeout=8)
    except Exception:
        fetched = False
    counts = git("rev-list", "--left-right", "--count", f"HEAD...origin/{branch}")
    if counts:
        ahead, behind = counts.split()
        state = []
        if behind != "0":
            state.append(f"⚠ 원격보다 {behind}커밋 뒤 → 작업 전에 git pull --rebase --autostash")
        if ahead != "0":
            state.append(f"로컬에 푸시 안 한 커밋 {ahead}개")
        if not state:
            state.append("원격과 동일")
        out.append(f"브랜치 {branch}: " + " · ".join(state) + ("" if fetched else "  (fetch 실패 — 오프라인? 마지막 fetch 기준)"))

    log = git("log", "-4", "--date=format:%m-%d %H:%M",
              "--format=%h %ad %s%n      └ %(trailers:key=Worked-by,valueonly,separator=%x2C)")
    if log:
        out.append("최근 커밋 (누가 어디서):")
        for line in log.splitlines():
            if line.strip() == "└":
                line = "      └ (작업자 트레일러 없음)"
            out.append("  " + line)

    dirty = [l for l in git("status", "--porcelain").splitlines() if l.strip()]
    if dirty:
        harness = [l for l in dirty if re.search(r"\s(\.claude/|CLAUDE\.md|docs/)", l)]
        out.append(f"⚠ 커밋 안 된 변경 {len(dirty)}건" + (f" (하네스·문서 {len(harness)}건)" if harness else "")
                   + " — 지난 세션이 /wrap 없이 끝난 듯. 먼저 확인")

    state_md = ROOT / ".claude" / "STATE.md"
    if state_md.exists():
        text = state_md.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^## ▶ 다음 작업.*?$(.*?)(?=^## |\Z)", text, re.M | re.S)
        if m:
            items = [l.strip() for l in m.group(1).splitlines() if l.strip().startswith(("- [ ]", "###"))][:6]
            if items:
                out.append("STATE 다음 작업(앞 6줄):")
                out.extend("  " + i[:110] for i in items)

    # 내게 온 이슈 / 내가 올려 둔 이슈 (gh 있을 때만)
    try:
        import json
        mine = subprocess.run(["gh", "issue", "list", "--assignee", "@me", "--state", "open", "--limit", "5",
                               "--json", "number,title,labels"], cwd=str(ROOT), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=8)
        if mine.returncode == 0:
            items = json.loads(mine.stdout or "[]")
            if items:
                out.append(f"📨 내게 온 이슈 {len(items)}건 (→ /issue list):")
                for it in items:
                    labels = ",".join(l["name"] for l in it.get("labels", []))
                    out.append(f"  #{it['number']} [{labels}] {it['title'][:80]}")
            sent = subprocess.run(["gh", "issue", "list", "--author", "@me", "--state", "open", "--json", "number"],
                                  cwd=str(ROOT), capture_output=True, text=True, timeout=8)
            n = len(json.loads(sent.stdout or "[]")) if sent.returncode == 0 else 0
            if n:
                out.append(f"내가 올려 둔 열린 이슈 {n}건 — 상대 답이 왔는지 /issue list")
        else:
            out.append("이슈: gh 미로그인 또는 원격 접근 불가 — gh auth login (없으면 /issue 대신 STATE 결정 대기에)")
    except FileNotFoundError:
        out.append("이슈: gh CLI 없음 — setup/README.md 참고 (없어도 작업은 됨)")
    except Exception:
        pass

    enc = re.sub(r"[^A-Za-z0-9]", "-", str(ROOT))
    mem_link = pathlib.Path.home() / ".claude" / "projects" / enc / "memory"
    target = ROOT / ".claude" / "memory"
    try:
        linked = mem_link.exists() and mem_link.resolve() == target.resolve()
    except Exception:
        linked = False
    out.append("메모리: 홈 링크 → 저장소 .claude/memory 연결됨" if linked
               else "메모리: 홈 링크 없음 → `.claude/memory/MEMORY.md`를 직접 읽을 것 (연결은 python setup/common/link_memory.py)")

    print("\n".join(out))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # 세션을 막지 않는다
        print(f"[하네스] session_start 실패(무시 가능): {e}")
    sys.exit(0)
