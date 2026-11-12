#!/usr/bin/env bash
# 크래프트 앱 6종 CLI를 ~/.local/bin 에 설치하고 이 저장소의 .mcp.json 을 생성한다 (맥).
#
#   bash setup/mac/install-craft.sh              # 없는 CLI만 설치 + .mcp.json
#   bash setup/mac/install-craft.sh --force      # 전부 최신으로 다시 받기
#   bash setup/mac/install-craft.sh --mcp-only   # 설치 건너뛰고 .mcp.json만
#   bash setup/mac/install-craft.sh --with=figcraft,pdfcraft   # 선택 앱 CLI도 설치
#
# 선택 앱: figcraft(화면 시안·코드 내보내기) 는 .mcp.json 에도 등록, pdfcraft(PDF 주석·정리) 는 CLI만 설치한다
# (pdfcraft 는 MCP 도구가 많아 필요할 때 셸에서 pdfcraft-cli 로 쓴다). 한 번 넣은 figcraft 항목은 다음 실행에도 유지되고,
# --force 는 이미 깔려 있는 선택 앱 CLI도 같이 최신으로 올린다.
#
# GUI 앱(/Applications/<App>.app)은 https://getartcraft.com/download 런처로 설치하면 된다.
# CLI는 GitHub 릴리스(storytold/<app>)의 <app>-cli-<ver>-macos-universal.zip. 서명·공증되어 있음.
set -euo pipefail

APPS=(vectorcraft photocraft effectcraft designcraft filmcraft soundcraft)
BIN="$HOME/.local/bin"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OPTIONAL_APPS=(figcraft pdfcraft)   # 선택 앱: --with= 로 고른 것만 설치
FORCE=0; MCP_ONLY=0; LINK_ARGS=(); WITH=""
for a in "$@"; do case "$a" in --force) FORCE=1;; --mcp-only) MCP_ONLY=1;; --with=*) WITH="${a#*=}";; --who=*|--machine=*) LINK_ARGS+=("${a%%=*}" "${a#*=}");; esac; done
EXTRAS=()
for app in "${OPTIONAL_APPS[@]}"; do
  if [[ ",$WITH," == *",$app,"* ]] || [[ $FORCE -eq 1 && -x "$BIN/$app-cli" ]]; then EXTRAS+=("$app"); fi
done
for w in ${WITH//,/ }; do
  [[ " ${OPTIONAL_APPS[*]} " == *" $w "* ]] || echo "  모르는 선택 앱: $w (가능: ${OPTIONAL_APPS[*]})" >&2
done
# 예: bash setup/mac/install-craft.sh --mcp-only --who=<이름> --machine=mac  (안 주면 물어봄)

echo "저장소: $REPO_ROOT"
mkdir -p "$BIN"

install_cli() {
  local app="$1" cli="$BIN/$app-cli"
  if [[ -x "$cli" && $FORCE -eq 0 ]]; then echo "  [$app] 이미 있음: $cli"; return; fi
  local json url tag
  # 비인증 API는 시간당 60회라 쉽게 403 → gh 로그인돼 있으면 gh api, 아니면 GITHUB_TOKEN 있으면 실어 보냄
  if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
    json="$(gh api "repos/storytold/$app/releases/latest")" || { echo "  [$app] 릴리스 조회 실패(gh api)" >&2; return 1; }
  else
    local auth=(); [[ -n "${GITHUB_TOKEN:-}" ]] && auth=(-H "Authorization: Bearer $GITHUB_TOKEN")
    json="$(curl -fsSL -H 'User-Agent: claude-harness-setup' ${auth[@]+"${auth[@]}"} "https://api.github.com/repos/storytold/$app/releases/latest")" \
      || { echo "  [$app] 릴리스 조회 실패 — 403이면 API 한도(시간당 60회). gh auth login 또는 GITHUB_TOKEN 설정 후 다시" >&2; return 1; }
  fi
  tag="$(printf '%s' "$json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["tag_name"])')"
  url="$(printf '%s' "$json" | python3 -c '
import json,sys
for a in json.load(sys.stdin)["assets"]:
    if a["name"].endswith("-macos-universal.zip") and "-cli-" in a["name"]:
        print(a["browser_download_url"]); break')"
  if [[ -z "$url" ]]; then echo "  [$app] $tag 릴리스에 macOS CLI zip이 없음" >&2; return 1; fi
  echo "  [$app] $tag 다운로드…"
  local tmp; tmp="$(mktemp -d)"
  curl -fsSL "$url" -o "$tmp/cli.zip"
  unzip -oq "$tmp/cli.zip" -d "$tmp/x"
  local found; found="$(find "$tmp/x" -type f -name "$app-cli" | head -1)"
  if [[ -z "$found" ]]; then echo "  [$app] zip 안에 $app-cli 가 없음" >&2; rm -rf "$tmp"; return 1; fi
  install -m 755 "$found" "$cli"
  xattr -d com.apple.quarantine "$cli" 2>/dev/null || true
  rm -rf "$tmp"
  echo "  [$app] 설치 완료: $cli ($("$cli" --version 2>/dev/null | head -1))"
}

FAILED=""
if [[ $MCP_ONLY -eq 0 ]]; then
  for app in "${APPS[@]}" ${EXTRAS[@]+"${EXTRAS[@]}"}; do install_cli "$app" || FAILED="$FAILED $app"; done
fi

# .mcp.json 생성 — 실패한 앱이 있는데 기존 파일이 있으면 덮어쓰지 않는다(기존 MCP 연결이 사라지지 않게)
CRAFT_FAILED="$FAILED" CRAFT_WITH="$WITH" python3 - "$REPO_ROOT" "$BIN" "${APPS[@]}" <<'PY'
import json, os, sys
root, bin_dir, *apps = sys.argv[1:]
failed = os.environ.get("CRAFT_FAILED", "").split()
path = os.path.join(root, ".mcp.json")
# 선택 앱 figcraft: --with 로 골랐거나 기존 .mcp.json 에 이미 있으면 등록한다(pdfcraft 는 CLI만 쓰므로 등록하지 않는다)
try:
    with open(path, encoding="utf-8") as f:
        had = set(json.load(f).get("mcpServers", {}))
except (OSError, ValueError):
    had = set()
if "figcraft" in os.environ.get("CRAFT_WITH", "").split(",") or "figcraft" in had:
    apps.append("figcraft")
servers = {}
for app in apps:
    cli = os.path.join(bin_dir, f"{app}-cli")
    if not os.access(cli, os.X_OK):
        print(f"  [{app}] CLI 없음 — .mcp.json에서 제외", file=sys.stderr); continue
    args = ["mcp"]
    if app != "filmcraft":  # filmcraft-cli에는 root 옵션이 없다
        args += ["--automation-read-root", root, "--automation-write-root", root]
    servers[app] = {"type": "stdio", "command": cli, "args": args, "env": {}}
if os.path.exists(path) and (failed or not servers):
    print(f"\n.mcp.json 유지: 실패한 앱이 있어 덮어쓰지 않음 ({', '.join(failed) or 'CLI 0개'}). 원인을 고친 뒤 다시 실행")
    sys.exit(0)
with open(path, "w", encoding="utf-8") as f:
    json.dump({"mcpServers": servers}, f, ensure_ascii=False, indent=2); f.write("\n")
print(f"\n.mcp.json 생성: {path} ({len(servers)}개 서버)")
PY

mkdir -p "$REPO_ROOT"/craft/{vector,photo,effect,design,film,sound,out}

echo
echo "신원 설정 + 메모리 링크 (setup/common/link_memory.py):"
python3 "$REPO_ROOT/setup/common/link_memory.py" ${LINK_ARGS[@]+"${LINK_ARGS[@]}"}

cat <<'EOF'

다음 단계:
  1. 이 폴더에서 claude 를 (다시) 실행하면 MCP 서버 승인 창이 뜸 → 전부 허용
  2. 세션 시작 훅이 [하네스] 블록을 찍음 → '메모리: … 연결됨' 확인. /mcp 입력 → 6종이 connected 인지 확인
EOF
