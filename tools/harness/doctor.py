#!/usr/bin/env python3
"""하네스 자가 점검 — 설치가 끝났는지, 규약이 깨진 데가 없는지 한 번에. OK / WARN / FAIL 로 보고.

    python tools/harness/doctor.py          (맥은 python3)

"판정 불가"는 "정상"으로 돌려주지 않는다 — 확인 못 한 건 WARN 으로 남긴다. 표준 라이브러리만.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or pathlib.Path(__file__).resolve().parents[2])
R = []


def rep(level, name, detail=""):
    R.append((level, name, detail))


def git(*a):
    try:
        return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=10).stdout.strip()
    except Exception:
        return ""


def check_identity():
    who, mach = git("config", "harness.who"), git("config", "harness.machine")
    rep("OK" if who and mach else "FAIL", "커밋 신원 harness.who/machine", f"{who or '?'}@{mach or '?'}" + ("" if who and mach else " → python setup/common/link_memory.py"))
    hp = git("config", "core.hooksPath")
    rep("OK" if hp == ".githooks" else "FAIL", "git 훅 경로 .githooks", hp or "미설정 → link_memory.py 재실행")
    for f in ("prepare-commit-msg", "pre-commit"):
        p = ROOT / ".githooks" / f
        rep("OK" if p.exists() else "FAIL", f"훅 파일 {f}", "" if p.exists() else "없음")
    rep("OK" if git("config", "pull.rebase") == "true" else "WARN", "pull.rebase=true", "미설정이면 pull 이 merge 커밋을 만든다 → link_memory.py")


def check_memory():
    mem = ROOT / ".claude" / "memory"
    enc = re.sub(r"[^A-Za-z0-9]", "-", str(ROOT))
    link = pathlib.Path.home() / ".claude" / "projects" / enc / "memory"
    try:
        linked = link.exists() and link.resolve() == mem.resolve()
    except Exception:
        linked = False
    rep("OK" if linked else "WARN", "메모리 홈 링크", "" if linked else f"{link} 가 저장소를 가리키지 않음 → link_memory.py (세션은 저장소 루트에서)")
    idx = mem / "MEMORY.md"
    if not idx.exists():
        rep("FAIL", "MEMORY.md 색인", "없음")
        return
    text = idx.read_text(encoding="utf-8", errors="replace")
    linked_files = set(re.findall(r"\]\(([^)]+\.md)\)", text))
    files = {p.name for p in mem.glob("*.md") if p.name not in ("MEMORY.md", "README.md") and not p.name.startswith("local_")}
    orphan = files - linked_files
    dead = linked_files - {p.name for p in mem.glob("*.md")}
    rep("OK" if not orphan and not dead else "WARN", "메모리 색인 ↔ 파일 1:1",
        (f"색인 없음: {sorted(orphan)} " if orphan else "") + (f"파일 없음: {sorted(dead)}" if dead else ""))
    for p in mem.glob("*.md"):
        if p.name in ("MEMORY.md", "README.md"):
            continue
        body = p.read_text(encoding="utf-8", errors="replace")
        head = body[:400]
        if not head.startswith("---") or "description:" not in head:
            rep("WARN", f"메모리 프론트매터 {p.name}", "--- / name / description / metadata.type 필요")
        if p.name.startswith(("feedback_", "project_")) and "**Evidence:**" not in body:
            rep("WARN", f"메모리 근거 없음 {p.name}", "**Evidence:** (관찰한 사실·날짜) 줄을 넣는다 — 규약 .claude/memory/README.md")


def check_docs():
    for f in ("BRAIN.md", "STATE.md"):
        p = ROOT / ".claude" / f
        if not p.exists():
            rep("FAIL", f, "없음"); continue
        m = re.search(r"마지막 갱신:\s*(\d{4}-\d{2}-\d{2})", p.read_text(encoding="utf-8", errors="replace"))
        rep("OK" if m else "WARN", f"{f} '마지막 갱신' 날짜", m.group(1) if m else "표기 없음")
    s = (ROOT / ".claude" / "STATE.md").read_text(encoding="utf-8", errors="replace") if (ROOT / ".claude" / "STATE.md").exists() else ""
    unowned = [l for l in s.splitlines() if l.strip().startswith("- [ ]") and not re.search(r"`\[[^\]]+\]`", l)]
    rep("OK" if not unowned else "WARN", "STATE 미완료 항목 담당 표기", "" if not unowned else f"{len(unowned)}건에 `[이름]` 없음")
    log = re.search(r"## ✅ 완료 로그(.*)", s, re.S)
    if log and log.group(1).count("\n- ") > 15:
        rep("WARN", "STATE 완료 로그 길이", "15건 초과 — 오래된 것은 docs/log/ 로 옮긴다 (/checkpoint)")


def check_settings():
    p = ROOT / ".claude" / "settings.json"
    try:
        cfg = json.loads(p.read_text(encoding="utf-8"))
        rep("OK", "settings.json 파싱")
    except Exception as e:
        rep("FAIL", "settings.json 파싱", str(e)); return
    for script in ("session_start.py", "pending.py", "pre_gate.py"):
        q = ROOT / "tools" / "harness" / script
        rep("OK" if q.exists() else "FAIL", f"훅 스크립트 {script}", "" if q.exists() else "없음")
    mcp = ROOT / ".mcp.json"
    if not mcp.exists():
        rep("WARN", ".mcp.json", "없음 → MCP 를 쓰면 setup/ 스크립트로 생성 (없어도 작업은 됨)")
    else:
        try:
            servers = json.loads(mcp.read_text(encoding="utf-8"))["mcpServers"]
            missing = [k for k, v in servers.items() if not pathlib.Path(v["command"]).exists()]
            enabled = set(cfg.get("enabledMcpjsonServers", []))
            rep("OK" if not missing else "FAIL", f".mcp.json CLI 경로 {len(servers)}개", "" if not missing else f"없는 실행파일: {missing}")
            extra = set(servers) - enabled
            rep("OK" if not extra else "WARN", "MCP 허용 목록", "" if not extra else f"settings.json enabledMcpjsonServers 에 없음: {sorted(extra)}")
        except Exception as e:
            rep("WARN", ".mcp.json 검사", f"판정 불가: {e}")
    attrs = ROOT / ".gitattributes"
    rep("OK" if attrs.exists() and "eol=lf" in attrs.read_text(encoding="utf-8", errors="replace") else "WARN", ".gitattributes eol=lf", "")


def check_tools():
    rep("OK" if shutil.which("gh") else "WARN", "gh CLI", "" if shutil.which("gh") else "없음 → /issue 못 씀 (setup/README.md)")
    if shutil.which("gh"):
        try:
            r = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=8)
            rep("OK" if r.returncode == 0 else "WARN", "gh 로그인", "" if r.returncode == 0 else "gh auth login")
        except Exception:
            rep("WARN", "gh 로그인", "판정 불가")
    rep("OK" if sys.version_info >= (3, 7) else "FAIL", "python", sys.version.split()[0])


def main():
    for fn in (check_identity, check_memory, check_docs, check_settings, check_tools):
        try:
            fn()
        except Exception as e:
            rep("WARN", fn.__name__, f"검사 자체가 실패: {e}")
    icon = {"OK": "✅", "WARN": "⚠️ ", "FAIL": "❌"}
    for lv, name, det in R:
        print(f"{icon[lv]} [{lv}] {name}" + (f" — {det}" if det else ""))
    n = {k: sum(1 for r in R if r[0] == k) for k in ("OK", "WARN", "FAIL")}
    print(f"\n== OK {n['OK']} / WARN {n['WARN']} / FAIL {n['FAIL']} ==")
    return 1 if n["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
