# optional/film — 영상 프로젝트 모듈 (film/ 아래 채널·시리즈)

`mini-project/film/_template`(2026-10-21~27)을 흡수한 것. `film/` 상위 폴더의 CLAUDE.md·README.md(폴더 관례·시리즈 규칙·포트 배정표·도구 업데이트)는 그대로 film에 있고, 이 모듈은 **프로젝트 하나의 뼈대**만 준다. 보통 `craft` 모듈과 같이 켠다.

## 켜기

```bash
python3 <harness>/setup/sync.py init film/<이름> --profile solo --with film,craft --title "<채널 이름>"
```

하는 일: `.claude/commands/update.md`(`/update`, 공용) · `tools/craft.sh`(브리지 포트로 앱 열기 — 포트는 `.mcp.json`에서 읽음, 공용) · CLAUDE.md에 "영상 프로젝트" 절 · settings.json에 `film/tools/update-check.sh --quiet` 훅 · `docs/{00_채널,01_회차,02_아이디어,03_편집}` `media/{원본,내보내기/…}` `edit/{film,effect,motion}` 폴더 · 영상용 BRAIN/STATE 뼈대 · `.mcp.json`(브리지 포트 자리표시자 — `film/README.md` 배정표대로 채운다).

`film/` 밖에 켜면(상위 `README.md`·`tools/update-check.sh`가 없으면) 업데이트 훅·포트 배정 줄을 넣지 않고 headless `.mcp.json`을 쓴다. 유튜브 회차형이 아닌 SNS 게시물 채널이면 film 대신 [`post`](../post/README.md) 모듈.

## 공용 vs 소유

| 공용 (sync가 갱신) | 소유 (한 번 만들고 프로젝트가 관리) |
|---|---|
| `.claude/commands/update.md`, `tools/craft.sh` | CLAUDE.md 절, settings.json 훅, `.mcp.json`, BRAIN/STATE(`skeleton/`) |

`CLAUDE.snippet.md`·`settings.snippet.json`·`mcp.json.example`·`skeleton/`이 바뀌면 sync가 "✎ 수동 확인"으로 알려 준다. craft 모듈과 같이 켜면 크래프트 CLAUDE 절은 생략된다(영상 절이 `edit/` 폴더 관례·브리지 포트를 대신 설명).
