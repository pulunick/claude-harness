#!/usr/bin/env python3
"""하네스 모듈 표 — 무엇이 '공용 파일'(하네스가 소유, sync.py가 덮어씀)이고, 모듈을 켤 때 한 번만 무엇을 하는지.

두 층:
  - 공용 파일   : 아래 MODULES 에 적힌 (하네스 경로 → 프로젝트 경로). 프로젝트에서 직접 고치지 않는다.
                  고칠 일이 생기면 하네스에서 고치고 커밋한 뒤 `setup/sync.py --all` 로 전파한다.
  - 프로젝트 소유: CLAUDE.md · .claude/BRAIN.md · .claude/STATE.md · .claude/settings.json · .mcp.json · 메모리.
                  켤 때 한 번 만들거나(enable) 조각을 합치고(snippet), 그 뒤로는 sync 가 손대지 않는다.
                  조각(CLAUDE.snippet.md, settings.snippet.json)이 하네스에서 바뀌면 sync 가 "수동 확인" 으로 알려만 준다.

프로필: solo(혼자, git 선택) / team(여럿이 한 저장소 — /start·/wrap·훅·공유 메모리).
표준 라이브러리만. init.py 와 sync.py 가 같이 쓴다.
"""
import datetime
import json
import os
import shutil
from pathlib import Path

HARNESS = Path(__file__).resolve().parent.parent
MANIFEST = ".claude/harness.json"
REGISTRY = Path.home() / ".claude" / "harness-projects.txt"
HOME_FILE = Path.home() / ".claude" / "harness-home"

# SessionStart 훅 한 줄 — 하네스가 있는 기기에서만 동작, 없으면 침묵(fail-open). 모든 프로필의 settings.json 에 들어간다.
CHECK_HOOK = ("sh -c 'h=$(cat ~/.claude/harness-home 2>/dev/null); [ -n \"$h\" ] && [ -f \"$h/setup/sync.py\" ] "
              "&& python3 \"$h/setup/sync.py\" --check \"$CLAUDE_PROJECT_DIR\"; exit 0'")

OWNED = ["CLAUDE.md", ".claude/BRAIN.md", ".claude/STATE.md", ".claude/settings.json", ".mcp.json"]


def _same(*rels):
    return [(r, r) for r in rels]


# 모듈 → 공용 파일. "files" 는 모든 프로필, "files_team" 은 team 프로필에서만 추가로.
MODULES = {
    "core": {
        # doc-keeper 에이전트는 프로젝트 문서 목록을 품으므로 소유 파일(프로필 뼈대에서 한 번 생성)
        "files": _same(".claude/commands/checkpoint.md", ".claude/commands/role.md"),
        "snippets": ["profiles/solo/.claude/agents/doc-keeper.md", "profiles/solo/CLAUDE.md"],
    },
    "team": {
        "files": _same(
            ".claude/commands/start.md", ".claude/commands/wrap.md", ".claude/commands/issue.md",
            "tools/harness/session_start.py", "tools/harness/pending.py", "tools/harness/pre_gate.py", "tools/harness/doctor.py",
            ".githooks/pre-commit", ".githooks/prepare-commit-msg",
            "setup/common/link_memory.py", "setup/common/statusline.py", "setup/common/claude-settings.example.json",
            ".claude/memory/README.md", ".github/ISSUE_TEMPLATE/problem.md", ".github/PULL_REQUEST_TEMPLATE.md",
            ".gitattributes", "AGENTS.md",
        ),
        # 자리표시자({{…}})가 들어가 init 때 치환되는 파일은 소유 — 바뀌면 알려만 준다
        "snippets": [".claude/settings.json", "CLAUDE.md", "setup/README.md", "setup/windows/bootstrap-prompt.md",
                     ".claude/BRAIN.md", ".claude/STATE.md", ".claude/agents/doc-keeper.md"],
    },
    "mockup": {
        "files": _same(".claude/commands/mockup.md", "tools/build_mockup.py"),
        "snippets": [],
    },
    "craft": {
        "files": [],
        "files_team": [
            ("optional/craft/setup/mac/install-craft.sh", "setup/mac/install-craft.sh"),
            ("optional/craft/setup/windows/install-craft.ps1", "setup/windows/install-craft.ps1"),
            ("optional/craft/skills/craft/SKILL.md", ".claude/skills/craft/SKILL.md"),
        ],
        "snippets": ["optional/craft/CLAUDE.snippet.md", "optional/craft/CLAUDE.snippet.solo.md"],
    },
    "film": {
        "files": [
            ("optional/film/commands/update.md", ".claude/commands/update.md"),
            ("optional/film/tools/craft.sh", "tools/craft.sh"),
        ],
        "snippets": ["optional/film/CLAUDE.snippet.md", "optional/film/settings.snippet.json", "optional/film/mcp.json.example",
                     "optional/film/skeleton"],
    },
}

PROFILE_DEFAULTS = {"solo": ["core"], "team": ["core", "team", "mockup"]}


def files_of(module, profile):
    m = MODULES[module]
    return list(m["files"]) + (list(m.get("files_team", [])) if profile == "team" else [])


def all_files(modules, profile):
    out = []
    for mod in modules:
        out += files_of(mod, profile)
    return out


def snippets_of(modules):
    out = []
    for mod in modules:
        out += MODULES[mod]["snippets"]
    return out


# ---------- manifest / registry ----------

def read_manifest(root):
    p = Path(root) / MANIFEST
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def write_manifest(root, profile, modules, commit):
    p = Path(root) / MANIFEST
    p.parent.mkdir(parents=True, exist_ok=True)
    data = {"harness": "https://github.com/pulunick/claude-harness", "profile": profile,
            "modules": list(dict.fromkeys(modules)), "commit": commit,
            "synced": datetime.date.today().isoformat()}
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


def register(root):
    root = str(Path(root).resolve())
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    lines = REGISTRY.read_text(encoding="utf-8").splitlines() if REGISTRY.exists() else []
    if root not in lines:
        lines.append(root)
        REGISTRY.write_text("\n".join(lines) + "\n", encoding="utf-8")
    HOME_FILE.write_text(str(HARNESS) + "\n", encoding="utf-8")


def registered():
    if not REGISTRY.exists():
        return []
    return [l for l in REGISTRY.read_text(encoding="utf-8").splitlines() if l.strip() and Path(l).exists()]


# ---------- 한 번만 하는 설정 (enable) ----------

def _append_snippet(path, snippet_path, marker):
    body = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker in body:
        return False
    snippet = (HARNESS / snippet_path).read_text(encoding="utf-8")
    path.write_text(body.rstrip() + ("\n\n" if body else "") + snippet, encoding="utf-8")
    return True


def merge_settings(root, extra):
    """settings.json 에 hooks·enabledMcpjsonServers·permissions.allow 를 합친다(중복 없이). 나머지 키는 그대로."""
    p = Path(root) / ".claude" / "settings.json"
    cfg = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    for ev, entries in extra.get("hooks", {}).items():
        have = cfg.setdefault("hooks", {}).setdefault(ev, [])
        existing = {h.get("command") for e in have for h in e.get("hooks", [])}
        for e in entries:
            if any(h.get("command") not in existing for h in e.get("hooks", [])):
                have.append(e)
    if "enabledMcpjsonServers" in extra:
        cfg["enabledMcpjsonServers"] = list(dict.fromkeys(cfg.get("enabledMcpjsonServers", []) + extra["enabledMcpjsonServers"]))
    if extra.get("permissions", {}).get("allow"):
        allow = cfg.setdefault("permissions", {}).setdefault("allow", [])
        for a in extra["permissions"]["allow"]:
            if a not in allow:
                allow.append(a)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _gitignore_add(root, block, key):
    gi = Path(root) / ".gitignore"
    if not gi.exists():
        return
    g = gi.read_text(encoding="utf-8")
    if key not in g:
        gi.write_text(g.rstrip() + "\n\n" + block, encoding="utf-8")


def enable(module, root, profile, modules=()):
    """모듈을 켤 때 한 번만: CLAUDE.md 절, settings 조각, 폴더, .mcp.json 본. 공용 파일 복사는 sync.py 몫."""
    root = Path(root)
    notes = []
    if module == "craft":
        snip = "optional/craft/CLAUDE.snippet.md" if profile == "team" else "optional/craft/CLAUDE.snippet.solo.md"
        if "film" in modules:
            notes.append("크래프트 절은 film 절이 대신함 (edit/ 폴더 관례, 브리지 포트)")
        elif _append_snippet(root / "CLAUDE.md", snip, "## 크래프트 앱"):
            notes.append("CLAUDE.md 에 '크래프트 앱' 절")
        merge_settings(root, {"enabledMcpjsonServers": ["vectorcraft", "photocraft", "effectcraft", "designcraft", "filmcraft", "soundcraft"]})
        if "film" not in modules:  # film 은 edit/ 폴더 관례를 쓴다
            _gitignore_add(root, "# 크래프트 결과물 중 큰 것 (영상·오디오). 필요하면 개별로 git add -f\ncraft/out/*.mp4\ncraft/out/*.mov\ncraft/out/*.wav\n", "craft/out/")
            for d in ("craft/vector", "craft/photo", "craft/effect", "craft/design", "craft/film", "craft/sound", "craft/out", "img/candidates"):
                (root / d).mkdir(parents=True, exist_ok=True)
            _gitignore_add(root, "# 이미지 후보(로컬 보관)\nimg/candidates/\n", "img/candidates/")
        if profile == "solo" and not (root / ".mcp.json").exists():
            ex = (HARNESS / "optional/craft/mcp.json.example").read_text(encoding="utf-8")
            (root / ".mcp.json").write_text(ex.replace("<프로젝트 절대경로>", str(root.resolve())), encoding="utf-8")
            notes.append(".mcp.json (headless 6종, 이 폴더로 루트 제한)")
        notes.append("team 이면 각 기기에서 setup/<os>/install-craft.* 실행" if profile == "team" else "세션 재시작 후 MCP 승인")
    elif module == "film":
        if _append_snippet(root / "CLAUDE.md", "optional/film/CLAUDE.snippet.md", "## 영상 프로젝트"):
            notes.append("CLAUDE.md 에 '영상 프로젝트' 절")
        merge_settings(root, json.loads((HARNESS / "optional/film/settings.snippet.json").read_text(encoding="utf-8")))
        for d in ("docs/00_채널", "docs/01_회차", "docs/02_아이디어", "docs/03_편집", "media/원본", "media/내보내기/영상",
                  "media/내보내기/썸네일", "media/내보내기/이미지", "edit/film", "edit/effect", "edit/motion", "tools"):
            (root / d).mkdir(parents=True, exist_ok=True)
        # 영상용 BRAIN/STATE 뼈대는 optional/film/skeleton/ — install_profile 이 자리표시자를 채워 만든다
        if not (root / ".mcp.json").exists():
            ex = (HARNESS / "optional/film/mcp.json.example").read_text(encoding="utf-8")
            (root / ".mcp.json").write_text(ex.replace("<프로젝트 절대경로>", str(root.resolve())), encoding="utf-8")
            notes.append(".mcp.json — <film포트>·<effect포트> 를 film/README.md 배정표대로 채울 것")
    elif module == "mockup":
        (root / "docs" / "design").mkdir(parents=True, exist_ok=True)
    return notes


def fill(text, values):
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def install_profile(root, profile, values, modules=()):
    """프로젝트 소유 파일을 뼈대에서 만든다 — 이미 있으면 건너뛴다(기존 프로젝트에 입힐 때 안전).
    모듈 뼈대(optional/<m>/skeleton/, 예: film 의 영상용 BRAIN/STATE)가 프로필 뼈대보다 먼저 온다."""
    root = Path(root)
    roots = [HARNESS / "optional" / m / "skeleton" for m in modules if (HARNESS / "optional" / m / "skeleton").is_dir()]
    roots.append(HARNESS / "profiles" / profile)
    made = []
    for src_root in roots:
        for p in src_root.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(src_root)
            dst = root / rel
            if dst.exists():
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(fill(p.read_text(encoding="utf-8"), values), encoding="utf-8")
            made.append(str(rel))
    # settings.json 이 이미 있던 프로젝트에도 하네스 점검 훅은 넣는다
    merge_settings(root, {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": CHECK_HOOK}]}]}})
    return made
