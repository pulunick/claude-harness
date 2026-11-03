#!/usr/bin/env python3
"""PreToolUse(Bash) 훅 — 파괴적·규칙 위반 git 명령을 물리적으로 막는다. 문서에 "금지"라고 적는 것과 다르다.

stdin 으로 훅 JSON({"tool_input":{"command": ...}})을 받는다. 막을 땐 exit 2 + stderr 사유(Claude 에게 전달됨).
그 외·판단 불가는 exit 0(fail-open). 표준 라이브러리만.
"""
import json
import re
import sys

# git 과 하위 명령 사이의 전역 옵션(-C 경로, -c k=v, --git-dir= 등)도 건너뛴다. [^;&|\n]* = 같은 명령 조각 안에서만
G = r"\bgit(?:\s+(?:-C|-c)\s+\S+|\s+--[a-z-]+(?:=\S+)?)*\s+"
SEG = r"[^;&|\n]*"

RULES = [
    (G + r"push\b" + SEG + r"\s(?:--force(?!-with-lease)\b|-f\b)", "강제 푸시 금지 — 상대 커밋이 날아간다. pull --rebase 후 다시 푸시"),
    (G + r"push\b" + SEG + r"\s\+\S", "+refspec 강제 푸시 금지 — pull --rebase 후 다시 푸시"),
    (G + r"push\b" + SEG + r"--force-with-lease", "force-with-lease 도 금지 — 사용자가 명시 허락한 경우에만 사용자 손으로"),
    (G + r"reset\s+--hard\b", "reset --hard 금지 — 작업 손실. git stash 나 git restore <파일> 로"),
    (G + r"clean\s+-[a-zA-Z]*f", "clean -f 금지 — 추적 안 된 후보 이미지·설정이 지워진다"),
    (G + r"branch\s+-D\b", "branch -D 금지 — -d 로 (머지 안 된 브랜치면 사용자에게)"),
    (G + r"(?:commit|push)\b" + SEG + r"--no-verify", "--no-verify 금지 — 훅이 막는 데는 이유가 있다. 규칙 쪽을 고친다"),
    (G + r"add\s+(?:-A|--all|\.|-u|:/)(?:\s|$)", "자동 스테이징 금지 — 파일을 명시 나열한다 (/wrap 4절)"),
    (G + r"commit\b" + SEG + r"\s(?:-[b-zA-Z]*a[a-zA-Z]*|--all)(?:\s|$)", "commit -a 금지 — 추적 파일 전부가 스테이징된다. git add <파일> 후 commit"),
    (G + r"rebase\s+-i\b", "대화형 rebase 는 이 환경에서 안 된다"),
    (G + r"(?:checkout\s+(?:--\s+)?\.|restore\s+\.)(?:\s|$)", "작업 트리 전체 되돌리기 금지 — 파일을 지정한다"),
    (G + r"stash\s+clear\b", "stash clear 금지 — 보관한 작업이 전부 지워진다. drop <번호> 로 하나씩(사용자 확인 후)"),
]


def strip_text(cmd):
    """커밋 메시지·heredoc 본문 속 글자("--no-verify 금지" 같은 문구)로 오탐하지 않게 따옴표·heredoc 내용을 비운다."""
    cmd = re.sub(r"<<-?\s*['\"]?(\w+)['\"]?[^\n]*\n.*?\n\s*\1(?=\s|$)", "<<HEREDOC", cmd, flags=re.S)
    cmd = re.sub(r"'[^']*'", "''", cmd)
    return re.sub(r'"(?:[^"\\]|\\.)*"', '""', cmd)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    cmd = (data.get("tool_input") or {}).get("command") or ""
    if not cmd:
        return 0
    bare = strip_text(cmd)
    for pat, why in RULES:
        if re.search(pat, bare):
            sys.stderr.write(f"[하네스 pre_gate] 차단: {why}\n  명령: {cmd[:160]}\n")
            return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
