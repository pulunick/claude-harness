#!/bin/zsh
# ArtCraft 앱을 Claude Code 제어 포트로 열기 — 포트는 프로젝트 .mcp.json 의 --bridge 값을 읽는다 (하네스 공용 파일, 프로젝트에서 고치지 않음)
# 사용: tools/craft.sh film|effect|vector
# PhotoCraft·DesignCraft·SoundCraft는 앱 없이(헤드리스) 연결되므로 열 필요 없음. VectorCraft는 앱이 꺼져 있으면 헤드리스로 자동 전환
ROOT="${0:A:h:h}"
case "$1" in
  film)   app=FilmCraft   server=filmcraft ;;
  effect) app=EffectCraft server=effectcraft ;;
  vector) app=VectorCraft server=vectorcraft ;;
  *) echo "사용법: tools/craft.sh film|effect|vector"; exit 1 ;;
esac
port=$(python3 - "$ROOT/.mcp.json" "$server" <<'EOF'
import json, re, sys
try:
    s = json.dumps(json.load(open(sys.argv[1]))["mcpServers"][sys.argv[2]])
    m = re.search(r'--bridge["\s,]+(?:127\.0\.0\.1:)?(\d+)', s)
    print(m.group(1) if m else "")
except Exception:
    print("")
EOF
)
[[ -n $port ]] || { echo "$server 의 --bridge 포트를 .mcp.json 에서 못 찾음 (film/README.md 배정표대로 적을 것)"; exit 1; }

if pgrep -xq "$app"; then
  echo "$app 이(가) 이미 켜져 있음. 종료(Cmd+Q) 후 다시 실행"
  exit 1
fi
# FilmCraft 0.13+는 FILMCRAFT_CONTROL_TOKEN(64자리 hex) 없이 제어 포트를 열지 않는다. MCP(.mcp.json)도 같은 파일을 읽는다
if [[ $app == FilmCraft ]]; then
  tok=~/.config/artcraft/filmcraft-control-token
  [[ -s $tok ]] || { mkdir -p -m 700 ${tok:h}; openssl rand -hex 32 > $tok; chmod 600 $tok; }
  open --env FILMCRAFT_CONTROL_TOKEN=$(<$tok) -a "$app" --args --control "$port"
else
  open -a "$app" --args --control "$port"
fi
echo "$app → 포트 $port"
