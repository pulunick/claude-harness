#!/usr/bin/env python3
"""PreToolUse(Bash) 훅 — 파괴적·규칙 위반 git 명령을 물리적으로 막는다. 문서에 "금지"라고 적는 것과 다르다.

stdin 으로 훅 JSON({"tool_input":{"command": ...}})을 받는다. 막을 땐 exit 2 + stderr 사유(Claude 에게 전달됨).
통과는 exit 0. 스크립트 자체 오류는 exit 1 → 훅 설정의 onFailure:"block" 이 그 git 명령을 막는다(고장 난 가드가 조용히 통과시키지 않게).
명령이 비었으면 exit 0. 표준 라이브러리만.

판정은 정규식이 아니라 토큰으로 한다: 명령을 조각(; & | 줄바꿈 괄호)으로 나누고, 조각마다 git 하위 명령과
옵션 집합을 읽는다. 옵션 순서(`reset HEAD~1 --hard`)·묶음(`push -uf`)·짧은 꼴(`commit -n`)이 달라도 같은 판정이 나온다.
규칙을 고치면 `python3 tools/harness/test_pre_gate.py` 로 확인한다.
"""
import json
import re
import sys

HEREDOC = re.compile(r"(<<-?\s*['\"]?(\w+)['\"]?[^\n]*)\n.*?\n\s*\2(?=\s|$)", re.S)
ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
WRAPPERS = {"command", "exec", "sudo", "env", "time", "noglob", "nohup", "builtin",
            "{", "then", "do", "else", "elif", "if", "while", "until", "!"}
SHELLS = {"sh", "bash", "zsh", "dash"}
GLOBAL_VALUED = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env", "--super-prefix"}
# 작업 트리 전체를 가리키는 경로 지정
WHOLE = {".", "*", ":", "./*", "**", ":/*", ":(top)", "./."}

# 하위 명령별: (값을 받는 짧은 옵션, 값이 붙어서만 오는 짧은 옵션, 값을 받는 긴 옵션)
SPEC = {
    "push": ("o", "", {"--repo", "--receive-pack", "--exec", "--push-option"}),
    "clean": ("e", "", {"--exclude"}),
    "branch": ("u", "", {"--set-upstream-to", "--contains", "--no-contains", "--merged", "--no-merged", "--sort", "--format", "--points-at"}),
    "commit": ("mFCct", "uS", {"--message", "--file", "--reuse-message", "--reedit-message", "--template", "--author", "--date",
                               "--fixup", "--squash", "--cleanup", "--trailer", "--pathspec-from-file"}),
    "add": ("", "", {"--chmod", "--pathspec-from-file"}),
    "checkout": ("bB", "", {"--orphan", "--conflict", "--pathspec-from-file"}),
    "switch": ("cC", "", {"--create", "--force-create", "--orphan", "--conflict"}),
    "restore": ("s", "", {"--source", "--conflict", "--pathspec-from-file"}),
    "rebase": ("sXx", "SC", {"--onto", "--exec", "--strategy", "--strategy-option", "--empty", "--whitespace"}),
}


def lex(cmd):
    """명령 문자열 → 조각 목록. 조각 = [(글자, 불투명)] — 불투명은 공백이 든 따옴표 문자열(메시지·본문)이라 옵션으로 보지 않는다."""
    cmd = HEREDOC.sub(lambda m: m.group(1), cmd)  # heredoc 본문만 비운다. 같은 줄의 뒤 명령(`<<EOF | git push -f`)은 남긴다
    segs, seg, cur, quoted = [], [], None, False
    i, n = 0, len(cmd)

    def end_tok():
        nonlocal cur, quoted
        if cur is not None:
            text = "".join(cur)
            seg.append((text, quoted and bool(re.search(r"\s", text))))
        cur, quoted = None, False

    def end_seg():
        nonlocal seg
        end_tok()
        if seg:
            segs.append(seg)
        seg = []

    while i < n:
        c = cmd[i]
        if c == "\\" and i + 1 < n:
            if cmd[i + 1] != "\n":
                cur = (cur or []) + [cmd[i + 1]]
            i += 2
            continue
        if c == "'":
            j = cmd.find("'", i + 1)
            j = n if j < 0 else j
            cur = (cur or []) + [cmd[i + 1:j]]
            quoted = True
            i = j + 1
            continue
        if c == '"':
            j, buf = i + 1, []
            while j < n and cmd[j] != '"':
                if cmd[j] == "\\" and j + 1 < n:
                    j += 1
                buf.append(cmd[j])
                j += 1
            cur = (cur or []) + buf
            quoted = True
            i = j + 1
            continue
        if c == "#" and cur is None:
            while i < n and cmd[i] != "\n":
                i += 1
            continue
        if c in " \t":
            end_tok()
        elif c in "\n;|&()`":
            end_seg()
        elif c == "$" and cmd[i + 1:i + 2] == "(":
            end_seg()
            i += 1
        else:
            cur = (cur or []) + [c]
        i += 1
    end_seg()
    return segs


def base(word):
    name = re.split(r"[\\/]", word)[-1].lower()
    return name[:-4] if name.endswith(".exe") else name


def parse(args, valued_short="", attached_short="", valued_long=()):
    """(긴 옵션 집합, 짧은 옵션 글자 집합, 위치 인자 목록). 값으로 쓰인 토큰은 옵션으로 세지 않는다."""
    longs, shorts, pos = set(), set(), []
    after_dd = skip = False
    for text, opaque in args:
        if skip:
            skip = False
        elif after_dd or opaque or not text.startswith("-") or text == "-":
            pos.append(text)
        elif text == "--":
            after_dd = True
        elif text.startswith("--"):
            name = text.split("=", 1)[0]
            longs.add(name)
            skip = name in valued_long and "=" not in text
        else:
            for j, ch in enumerate(text[1:], 1):
                if ch in attached_short:
                    break
                if ch in valued_short:
                    skip = j == len(text) - 1
                    break
                shorts.add(ch)
    return longs, shorts, pos


def whole_tree(pos):
    return any((p.rstrip("/") or "/") in WHOLE for p in pos)


def check_git(args):
    i = 0
    while i < len(args):
        t = args[i][0]
        if t in GLOBAL_VALUED:
            val = args[i + 1][0] if i + 1 < len(args) else ""
            if t in ("-c", "--config-env") and val.lower().startswith("core.hookspath"):
                return "core.hooksPath 바꿔치기 금지 — 훅을 끄는 것과 같다. 훅이 막으면 원인을 고친다"
            i += 2
        elif t.startswith("-"):
            i += 1
        else:
            break
    if i >= len(args):
        return None
    sub = args[i][0]
    longs, shorts, pos = parse(args[i + 1:], *SPEC.get(sub, ("", "", ())))
    dry = "--dry-run" in longs

    if "--no-verify" in longs or (sub == "commit" and "n" in shorts):
        return "--no-verify(-n) 금지 — 훅이 막는 데는 이유가 있다. 규칙 쪽을 고친다"
    if sub == "push":
        if longs & {"--force-with-lease", "--force-if-includes"}:
            return "force-with-lease 도 금지 — 사용자가 명시 허락한 경우에만 사용자 손으로"
        if "--force" in longs or "f" in shorts:
            return "강제 푸시 금지 — 상대 커밋이 날아간다. pull --rebase 후 다시 푸시"
        if any(p.startswith("+") for p in pos):
            return "+refspec 강제 푸시 금지 — pull --rebase 후 다시 푸시"
        if "--mirror" in longs:
            return "push --mirror 금지 — 원격의 다른 브랜치가 지워지거나 덮인다"
        if longs & {"--delete", "--prune"} or "d" in shorts or any(p.startswith(":") for p in pos):
            return "원격 브랜치 삭제 금지 — 사용자 손으로 (PR 브랜치는 gh pr merge --delete-branch)"
    elif sub == "reset":
        if "--hard" in longs:
            return "reset --hard 금지 — 작업 손실. git stash 나 git restore <파일> 로"
    elif sub == "clean":
        if ("--force" in longs or "f" in shorts) and not (dry or "n" in shorts):
            return "clean -f 금지 — 추적 안 된 후보 이미지·설정이 지워진다 (볼 거면 -n)"
    elif sub == "branch":
        if "D" in shorts or (("d" in shorts or "--delete" in longs) and ("f" in shorts or "--force" in longs)):
            return "branch -D 금지 — -d 로 (머지 안 된 브랜치면 사용자에게)"
    elif sub == "commit":
        if "a" in shorts or "--all" in longs:
            return "commit -a 금지 — 추적 파일 전부가 스테이징된다. git add <파일> 후 commit"
    elif sub == "add":
        if not (dry or "n" in shorts) and (shorts & {"A", "u"} or longs & {"--all", "--update", "--no-ignore-removal"}
                                           or whole_tree(pos)):
            return "자동 스테이징 금지 — 파일을 명시 나열한다(다른 세션의 미커밋 파일이 섞인다)"
    elif sub == "rebase":
        if "i" in shorts or "--interactive" in longs:
            return "대화형 rebase 는 이 환경에서 안 된다"
    elif sub == "checkout":
        if "f" in shorts or "--force" in longs or whole_tree(pos):
            return "작업 트리 전체 되돌리기 금지 — 파일을 지정한다 (checkout -f 포함)"
    elif sub == "switch":
        if "f" in shorts or longs & {"--force", "--discard-changes"}:
            return "switch -f/--discard-changes 금지 — 커밋 안 된 작업이 버려진다. stash 후 전환"
    elif sub == "restore":
        staged_only = ("S" in shorts or "--staged" in longs) and not ("W" in shorts or "--worktree" in longs)
        if not staged_only and whole_tree(pos):
            return "작업 트리 전체 되돌리기 금지 — 파일을 지정한다"
    elif sub == "stash":
        if pos[:1] == ["clear"]:
            return "stash clear 금지 — 보관한 작업이 전부 지워진다. drop <번호> 로 하나씩(사용자 확인 후)"
    return None


def check(cmd, depth=0):
    """막을 사유(문자열) 또는 None."""
    for seg in lex(cmd):
        while seg and not seg[0][1] and (ASSIGN.match(seg[0][0]) or seg[0][0] in WRAPPERS):
            seg = seg[1:]
        if not seg:
            continue
        name = base(seg[0][0])
        why = None
        if name == "xargs":
            idx = next((k for k, t in enumerate(seg) if k and base(t[0]) == "git"), None)
            if idx is not None:
                why = check_git(seg[idx + 1:])
        elif name == "git":
            why = check_git(seg[1:])
        elif depth < 3 and name == "eval":
            why = check(" ".join(t[0] for t in seg[1:]), depth + 1)
        elif depth < 3 and name in SHELLS:
            for k, (t, _) in enumerate(seg[1:-1], 1):
                if re.match(r"^-[a-zA-Z]*c$", t):
                    why = check(seg[k + 1][0], depth + 1)
                    break
        if why:
            return why
    return None


def main():
    data = json.load(sys.stdin)  # 못 읽으면 아래 except → exit 1
    cmd = (data.get("tool_input") or {}).get("command") or ""
    if not cmd:
        return 0
    why = check(cmd)
    if why:
        sys.stderr.write(f"[하네스 pre_gate] 차단: {why}\n  명령: {cmd[:160]}\n")
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        sys.stderr.write(f"[하네스 pre_gate] 가드 오류: {e}\n")
        sys.exit(1)
