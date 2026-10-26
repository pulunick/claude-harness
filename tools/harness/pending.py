#!/usr/bin/env python3
"""미커밋 변경 감지 — Stop 훅(advisory)과 /wrap 점검이 같은 구현을 쓴다.

    python tools/harness/pending.py          # 사람용 보고. 종료코드 0=없음 / 1=있음 / 2=확인 불가
    python tools/harness/pending.py --hook   # Stop 훅: {"systemMessage": ...}만 출력, 30분에 한 번, 어떤 예외에도 조용히 exit 0

"없음"과 "확인 불가"를 같은 값으로 돌려주지 않는다 — git이 깨졌을 때 "전부 커밋됨"으로 읽히면 이 스크립트가 있을 이유가 없다.
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or pathlib.Path(__file__).resolve().parents[2])
STATE_DIR = ROOT / ".claude" / ".harness_state"   # gitignore
NOTICE_INTERVAL = 30 * 60
HARNESS_RE = re.compile(r"\s(\.claude/|CLAUDE\.md|docs/)")


def pending():
    """(상태코드, 변경 목록). 2=확인 불가."""
    try:
        r = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=10)
    except Exception as e:
        return 2, [f"git 실행 실패: {e}"]
    if r.returncode != 0:
        return 2, [r.stderr.strip() or "git status 실패"]
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    return (1 if lines else 0), lines


def main():
    hook = "--hook" in sys.argv
    code, lines = pending()
    if not hook:
        if code == 2:
            print("[UNKNOWN] 확인 불가 — " + "; ".join(lines))
        elif code == 0:
            print("[OK] 커밋 안 된 변경 없음")
        else:
            harness = [l for l in lines if HARNESS_RE.search(l)]
            print(f"[PENDING] 미커밋 {len(lines)}건 (하네스·문서 {len(harness)}건)")
            for l in lines[:30]:
                print("  " + l)
        return code

    # Stop 훅: advisory, 쓰로틀
    if code != 1:
        return 0
    harness = [l for l in lines if HARNESS_RE.search(l)]
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = STATE_DIR / "pending_notice"
    prev_t, prev_n = 0.0, -1
    if stamp.exists():
        try:
            prev_t, prev_n = (float(x) for x in stamp.read_text().split())
        except Exception:
            pass
    if time.time() - prev_t < NOTICE_INTERVAL and len(lines) <= prev_n:
        return 0
    stamp.write_text(f"{time.time()} {len(lines)}")
    msg = f"[하네스] 커밋 안 된 변경 {len(lines)}건"
    if harness:
        msg += f" — 그중 BRAIN/STATE·메모리·문서 {len(harness)}건은 상대 기기에 아직 안 갔다"
    msg += ". 세션을 끝낼 거면 /wrap."
    print(json.dumps({"systemMessage": msg}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0 if "--hook" in sys.argv else 2)
