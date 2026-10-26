#!/usr/bin/env python3
"""PreToolUse(Bash) 훅 — 파괴적·규칙 위반 git 명령을 물리적으로 막는다. 문서에 "금지"라고 적는 것과 다르다.

stdin 으로 훅 JSON({"tool_input":{"command": ...}})을 받는다. 막을 땐 exit 2 + stderr 사유(Claude 에게 전달됨).
그 외·판단 불가는 exit 0(fail-open). 표준 라이브러리만.
"""
import json
import re
import sys

RULES = [
    (r"\bgit\s+push\b.*\s--force(?!-with-lease)\b|\bgit\s+push\b.*\s-f\b", "강제 푸시 금지 — 상대 커밋이 날아간다. pull --rebase 후 다시 푸시"),
    (r"\bgit\s+push\b.*--force-with-lease", "force-with-lease 도 금지 — 사용자가 명시 허락한 경우에만 사용자 손으로"),
    (r"\bgit\s+reset\s+--hard\b", "reset --hard 금지 — 작업 손실. git stash 나 git restore <파일> 로"),
    (r"\bgit\s+clean\s+-[a-zA-Z]*f", "clean -f 금지 — 추적 안 된 후보 이미지·설정이 지워진다"),
    (r"\bgit\s+branch\s+-D\b", "branch -D 금지 — -d 로 (머지 안 된 브랜치면 사용자에게)"),
    (r"\bgit\s+commit\b.*--no-verify|\bgit\s+push\b.*--no-verify", "--no-verify 금지 — 훅이 막는 데는 이유가 있다. 규칙 쪽을 고친다"),
    (r"\bgit\s+add\s+(-A|--all|\.|-u)(\s|$)", "자동 스테이징 금지 — 파일을 명시 나열한다 (/wrap 4절)"),
    (r"\bgit\s+rebase\s+-i\b", "대화형 rebase 는 이 환경에서 안 된다"),
    (r"\bgit\s+checkout\s+--\s+\.|\bgit\s+restore\s+\.(\s|$)", "작업 트리 전체 되돌리기 금지 — 파일을 지정한다"),
]


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    cmd = (data.get("tool_input") or {}).get("command") or ""
    if not cmd:
        return 0
    for pat, why in RULES:
        if re.search(pat, cmd):
            sys.stderr.write(f"[하네스 pre_gate] 차단: {why}\n  명령: {cmd[:160]}\n")
            return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
