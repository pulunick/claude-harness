#!/usr/bin/env python3
"""Claude Code statusLine - 컨텍스트(CW) / 5시간(5H) / 7일(7D) 사용량 + 모델 + git.

Claude Code 가 stdin 으로 넘겨주는 공식 세션 JSON 만 사용한다 (MoAI 불필요).
- context_window.used_percentage        : 컨텍스트 사용률 (모든 사용자)
- rate_limits.five_hour.used_percentage : 5시간 rate limit (Claude.ai Pro/Max, 첫 API 응답 후)
- rate_limits.seven_day.used_percentage : 7일 rate limit  (동일)
필드 부재/ null 은 우아하게 처리한다.

설정: ~/.claude/settings.json 의 statusLine.command 에서 이 파일을 python 으로 실행.
Windows(PowerShell) + Git Bash 양쪽 동작. 의존성: python 3.7+, git(선택).
"""
import sys
import json
import os
import time

R = "\033[0m"
DIM = "\033[2m"
CYAN = "\033[36m"
BLUE = "\033[34m"
MAG = "\033[35m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
WHITE = "\033[97m"


def clean_text(s):
    """JSON 에서 온 문자열의 손상된 서로게이트 문자 제거 (session_name 등에서 발생 가능)."""
    if not s:
        return s
    try:
        return s.encode("utf-8", "replace").decode("utf-8", "replace")
    except Exception:
        return ""


def color_for(p):
    if p is None:
        return DIM
    if p < 60:
        return GREEN
    if p < 85:
        return YELLOW
    return RED


def bar(p, width=10):
    """10칸 막대. 채움 ▓ / 빈칸 ░, 사용률에 따라 색."""
    if p is None:
        return DIM + "-" * width + R
    filled = max(0, min(width, round(p / 100 * width)))
    return color_for(p) + "▓" * filled + DIM + "░" * (width - filled) + R


def pct_str(p):
    if p is None:
        return DIM + "  -" + R
    return color_for(p) + f"{int(round(p)):3d}%" + R


def reset_in(ts):
    """resets_at(epoch 초)까지 남은 시간을 압축 표기. 예: 2h07m / 3d14h / 42m."""
    if not ts:
        return ""
    try:
        s = int(ts) - int(time.time())
    except Exception:
        return ""
    if s <= 0:
        return ""
    m = s // 60
    d, rem = divmod(m, 1440)
    h, m = divmod(rem, 60)
    if d:
        txt = f"{d}d{h}h"
    elif h:
        txt = f"{h}h{m:02d}m"
    else:
        txt = f"{max(m, 1)}m"
    return f" {DIM}({txt}){R}"


def git_branch(cwd):
    """현재 브랜치명. subprocess 없이 .git/HEAD 직접 파싱 (statusLine 타임아웃 회피).
    repo 아니면 빈 문자열. detached HEAD 는 short sha."""
    try:
        d = os.path.abspath(cwd)
        head = None
        for _ in range(8):  # 상위로 올라가며 .git 탐색
            g = os.path.join(d, ".git")
            if os.path.isdir(g):
                head = os.path.join(g, "HEAD")
                break
            if os.path.isfile(g):  # worktree/submodule: "gitdir: <path>"
                with open(g, encoding="utf-8") as f:
                    ln = f.read().strip()
                if ln.startswith("gitdir:"):
                    head = os.path.join(ln.split(":", 1)[1].strip(), "HEAD")
                break
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
        if not head or not os.path.isfile(head):
            return ""
        with open(head, encoding="utf-8") as f:
            ref = f.read().strip()
        if ref.startswith("ref: refs/heads/"):
            return ref[len("ref: refs/heads/"):]
        return ref[:7] if ref else ""
    except Exception:
        return ""


def main():
    try:
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except Exception:
        pass

    model = (data.get("model") or {}).get("display_name", "?")
    version = data.get("version")

    cw = data.get("context_window") or {}
    size = cw.get("context_window_size")
    size_lbl = "1M" if size == 1000000 else ("200K" if size == 200000 else (str(size) if size else ""))
    cw_pct = cw.get("used_percentage")

    rl = data.get("rate_limits") or {}
    five = (rl.get("five_hour") or {}).get("used_percentage")
    week = (rl.get("seven_day") or {}).get("used_percentage")
    five_rst = (rl.get("five_hour") or {}).get("resets_at")
    week_rst = (rl.get("seven_day") or {}).get("resets_at")

    cwd = (data.get("workspace") or {}).get("current_dir") or data.get("cwd") or "."
    folder = os.path.basename(cwd.rstrip("/\\")) or cwd
    cost = (data.get("cost") or {}).get("total_cost_usd")

    model_lbl = f"{CYAN}{model}{R}"
    if size_lbl:
        model_lbl += f" {DIM}({size_lbl}){R}"
    if version:
        model_lbl += f" {DIM}v{version}{R}"

    branch = git_branch(cwd)
    session_name = clean_text(data.get("session_name"))

    line1 = f"{model_lbl} {DIM}|{R} {BLUE}{folder}{R}"
    if branch:
        line1 += f" {DIM}|{R} {MAG}{branch}{R}"
    if session_name:
        line1 += f" {DIM}|{R} {WHITE}{session_name}{R}"

    parts = [f"{DIM}CW{R} {bar(cw_pct)} {pct_str(cw_pct)}"]
    if five is not None or week is not None:
        parts.append(f"{DIM}5H{R} {bar(five)} {pct_str(five)}{reset_in(five_rst)}")
        parts.append(f"{DIM}7D{R} {bar(week)} {pct_str(week)}{reset_in(week_rst)}")
    if cost:
        parts.append(f"{DIM}${cost:.2f}{R}")
    line2 = f" {DIM}|{R} ".join(parts)

    print(line1)
    print(line2)


if __name__ == "__main__":
    main()
