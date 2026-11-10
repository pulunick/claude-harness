#!/usr/bin/env python3
"""pre_gate.py 회귀 테스트 — 규칙을 고친 뒤 돌린다. 실패가 있으면 종료코드 1.

    python3 tools/harness/test_pre_gate.py

BLOCK 은 막혀야 하는 명령, ALLOW 는 통과해야 하는 명령(오탐 방지). 새 구멍·오탐을 발견하면 여기에 먼저 한 줄 더한다.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pre_gate import check  # noqa: E402

BLOCK = [
    # 강제 푸시·원격 삭제
    "git push --force", "git push -f", "git push -fu origin main", "git push origin main -uf", "git push origin main --force",
    "git push --force-with-lease", "git push --force-with-lease=main:abc123 origin main", "git push origin +main",
    "git push origin --delete main", "git push -d origin old", "git push origin :main", "git push --mirror",
    'git push "--force"', "git commit -m x && git push -f", "cat <<EOF | git push --force\nx\nEOF",
    # reset --hard
    "git reset --hard", "git reset HEAD~1 --hard", "git reset -q --hard", "git -C sub reset --hard",
    "git --no-pager reset --hard HEAD", "cd sub && git reset --hard", "(git reset --hard)", "GIT_PAGER=cat git reset --hard",
    "/usr/bin/git reset --hard", "command git reset --hard", "bash -c 'git reset --hard'", "sh -lc \"git reset --hard\"",
    "eval git reset --hard", "if true; then git reset --hard; fi",
    # clean
    "git clean -f", "git clean -fd", "git --no-pager clean -fd", "git clean -d -f", "git clean --force -d", "git clean -xdf",
    # branch
    "git branch -D x", "git branch --delete --force x", "git branch -d -f x",
    # 훅 우회
    "git commit --no-verify -m x", "git commit -n -m x", "git commit -nm x", "git push --no-verify",
    "git merge --no-verify other", "git -c core.hooksPath=/dev/null commit -m x",
    # 자동 스테이징
    "git add -A", "git add --all", "git add .", "git add ./", "git add *", "git add -- .", "git add src .", "git add -v -A",
    "git add -u", "git add :/", "git ls-files -m | xargs git add -A",
    "git commit -a", "git commit -am x", 'git commit -m "x" -a', "git commit --all -m x", "git commit --amend -a",
    # 대화형·되돌리기
    "git rebase -i HEAD~3", "git rebase --interactive main",
    "git checkout .", "git checkout -- .", "git checkout HEAD -- .", "git checkout -f", "git checkout -f main",
    "git switch -f main", "git switch --discard-changes main",
    "git restore .", "git restore -- .", "git restore --worktree .", "git restore --staged --worktree .", "git restore -s HEAD~1 .",
    "git stash clear",
]

ALLOW = [
    "git status", "git push", "git push origin main", "git push -u origin 하늘/offline-map", "git push origin main --follow-tags",
    "git push origin fix-a", "git push -n origin main", "git push origin main  # -f 는 안 씀",
    "git commit -m x", "git commit --amend --no-edit", "git commit -m 'add -A 금지, --no-verify 금지'", 'git commit -m "-a"',
    "git commit -m x --author='a <a@b>'", "git commit -m x -- a.txt", "git commit -uno -m x", "git commit -S -m x",
    "git commit -F - <<'MSG'\n하네스: reset --hard 설명\n\ngit add -A 금지\nMSG\ngit push origin main",
    'git commit -m "$(cat <<\'EOF\'\n하네스: git push --force 를 막는다\n\ngit add . 금지\nEOF\n)"',
    "git add .gitignore .claude/STATE.md", "git add a.py && rm -f b.tmp", "git add 'src/*.py'", "git add -A --dry-run",
    "git add -n .", "git reset HEAD~1", "git reset --soft HEAD~1", "git reset a.txt",
    "git clean -n -d", "git clean -nfd", "git branch -d merged", "git branch -u origin/main",
    "git checkout main", "git checkout -b new", "git checkout -- a.txt", "git checkout HEAD~1 -- docs/a.md", "git checkout -",
    "git switch main", "git switch -c 하늘/x", "git restore a.txt", "git restore --staged .", "git restore --source HEAD~1 a.txt",
    "git stash", "git stash -a", "git stash drop stash@{1}", "git stash pop",
    "git rebase main", "git pull --rebase --autostash", "git tag -a v1 -m x", "git diff HEAD -- .",
    "git log -5 | grep -f pats.txt", "git log --format='%h reset --hard' -3",
    'echo "git reset --hard 는 금지"', "grep -rn 'git add -A' docs", 'gh pr create --title "git push --force 막기"',
    "bash -c 'git status'", "ls -a . && rm -f x", "",
]


def main():
    bad = []
    for cmd in BLOCK:
        if not check(cmd):
            bad.append("통과함(막혀야 함): " + cmd)
    for cmd in ALLOW:
        why = check(cmd)
        if why:
            bad.append(f"막힘(통과해야 함): {cmd}  ← {why}")
    for b in bad:
        print("❌ " + b.replace("\n", "\\n"))
    print(f"== 차단 {len(BLOCK)}건 · 통과 {len(ALLOW)}건 중 실패 {len(bad)} ==")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
