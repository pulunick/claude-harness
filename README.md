# claude-harness — Claude Code 프로젝트의 작업 체계 (정본)

모든 프로젝트가 같은 뼈대(BRAIN/STATE·`/checkpoint`·훅)로 시작하고, 뼈대가 바뀌면 전부에 전파되게 하는 템플릿. 프로필 두 가지:

- **team** — 두 사람 이상이 각자 기기(맥/윈도우)에서 **같은 저장소**를 번갈아 작업. 인원수 제한은 없다 — 담당 표시·`Worked-by`·이슈 assignee가 이름 단위로 돈다. 아래 항목 전부
- **solo** — 혼자 작업(git 선택). BRAIN/STATE·`/checkpoint`·`/role`·doc-keeper·하네스 점검 훅만. `profiles/solo/`

## 두 층 — 공용 파일과 프로젝트 소유 파일

| | 무엇 | 누가 고치나 |
|---|---|---|
| **공용** | `.claude/commands/*.md`(checkpoint·role·start·wrap·issue·mockup), `tools/harness/*.py`, `.githooks/`, `setup/common/`, 모듈 스크립트(`tools/craft.sh` 등). 목록은 `setup/modules.py` | **여기서만.** 고쳐 커밋 → `python3 setup/sync.py --all` 로 전파 |
| **소유** | `CLAUDE.md`, `.claude/BRAIN.md`·`STATE.md`, `.claude/settings.json`, `.mcp.json`, `.claude/agents/doc-keeper.md`, 메모리 | 각 프로젝트. 켤 때 한 번 만들어 주고(`CLAUDE.snippet.md`·`settings.snippet.json`) 그 뒤 sync는 안 건드린다 — 조각이 바뀌면 "✎ 수동 확인"으로 알려만 준다 |

각 프로젝트의 `.claude/harness.json`이 프로필·모듈·기준 커밋을 담고, `~/.claude/harness-projects.txt`가 등록 목록, `~/.claude/harness-home`이 이 저장소 위치다(기기마다 `sync.py init`/`--register`가 쓴다). 세션 시작 훅이 뒤처짐을 한 줄로 알리고, `sync.py <프로젝트>`가 3-way(기준 커밋 버전 vs 프로젝트 파일 vs 최신)로 갱신한다 — 프로젝트에서 손댄 공용 파일은 덮어쓰지 않고 충돌로 보고한다(되가져가거나 `--force`).

```bash
python3 setup/sync.py --list                     # 등록된 프로젝트와 기준 커밋
python3 setup/sync.py --all [--dry-run]          # 전부 갱신
python3 setup/sync.py <프로젝트> [--force]        # 하나만
python3 setup/sync.py --check <프로젝트>          # 훅용 한 줄 (뒤처졌을 때만)
```

## solo 프로젝트 시작 (한 줄)

```bash
python3 ~/Desktop/mini-project/claude-harness/setup/sync.py init <폴더> --profile solo --with craft[,film] --title "<제목>" --desc "<한 줄>"
# 이미 돌아가는 프로젝트에 입힐 때는 --bare (CLAUDE.md 절·폴더 생성 생략, manifest·점검 훅·공용 파일만)
```

- **세션 플로우 고정**: `/start`(pull → 상황판 → 문서 → 할 일) ~ `/wrap`(체크포인트 → 메모리 → 커밋 → 푸시)
- **문서 하네스**: `.claude/BRAIN.md`(확정된 결정만) / `.claude/STATE.md`(진행 상태, 담당 표시) — 인수인계는 이 두 파일로
- **누가 어디서 했는지**: 커밋마다 `Worked-by: 이름@기기` 트레일러 — git 훅이 자동으로 붙인다
- **공유 메모리**: Claude 메모리 폴더를 저장소 `.claude/memory/`에 링크 → 한 사람의 Claude가 배운 것이 커밋으로 상대에게 간다
- **규칙은 글보다 장치로**: 금지 파일·비밀값·개인 절대경로는 `pre-commit`이 막고, `git push --force`·`reset --hard`·`git add -A` 같은 명령은 Claude 훅(`pre_gate.py`)이 막는다. `doctor.py`가 설치·규약을 한 번에 점검
- **서로 넘기기**: `/issue` — 막힌 것·결정·부탁을 GitHub 이슈로 상대 담당 지정. PR은 선택
- 윈도우 상대방용 **부트스트랩 프롬프트**: Git·Claude Code만 사람이 깔고 나머지는 Claude가 셋업

## team 프로젝트 시작 (3단계)

```bash
# 1. 이 템플릿으로 저장소 만들기 — GitHub "Use this template" 또는
gh repo create <owner>/<project> --private --template <owner>/claude-harness --clone
cd <project>

# 2. 자리표시자 채우기 (프로젝트명·GitHub 경로·멤버 이름:기기 목록, 첫 멤버 = 나). 인자 없이 실행하면 물어본다
python3 setup/init.py --project <project> --title "<한글 제목>" --owner <owner> \
    --members <나>:mac,<동료1>:win,<동료2>:mac

# 3. 내 기기 신원 + 메모리 링크 + git 훅 활성화, 그리고 첫 커밋
python3 setup/common/link_memory.py --who <나> --machine mac
claude      # → /start
```

`init.py`가 하는 일: `{{PROJECT}}` 같은 자리표시자를 전부 치환하고, 프로젝트용 README로 바꾸고, 오늘 날짜를 BRAIN/STATE에 찍고, `--with craft,…`로 모듈을 켜고, `.claude/harness.json`을 써서 이후 `sync.py`로 공용 파일을 받게 하고, `/issue`용 라벨 6종을 만드는 `gh` 명령을 알려 준다(`--labels`를 주면 직접 만든다). 다른 멤버에게는 `setup/windows/bootstrap-prompt.md`의 회색 박스를 메신저로 보내면 된다(이름 부분만 그 사람 것으로).

## 구성

| 경로 | 역할 |
|---|---|
| `CLAUDE.md` | 프로젝트 규칙 정본 (init 이 제목·이름을 채움). `AGENTS.md`는 다른 에이전트용 진입점 |
| `.claude/BRAIN.md` · `STATE.md` | 확정 / 진행. 뼈대만 있고 1~7장은 프로젝트가 채운다. 8장(작업 체계)은 이 하네스 설명 |
| `.claude/commands/` | `/start` `/wrap` `/checkpoint` `/role` `/issue` `/mockup` |
| `.claude/agents/doc-keeper.md` | BRAIN/STATE 갱신 전담 에이전트 (프로젝트 문서 목록을 품으므로 소유 파일) |
| `.claude/settings.json` | 훅(SessionStart·Stop·PreToolUse) + 읽기 전용 명령 허용 목록. 기기별 `settings.local.json`은 커밋 안 함 |
| `.claude/memory/` | 공유 메모리. 규약은 안의 README. `feedback_*` 3건은 협업 스타일 기본값 — 안 맞으면 지운다 |
| `.githooks/` | `prepare-commit-msg`(트레일러) · `pre-commit`(금지 파일·비밀값·절대경로) |
| `tools/harness/` | `session_start.py`(상황판) · `pending.py`(미커밋 알림) · `pre_gate.py`(파괴적 명령 차단) · `doctor.py`(점검) |
| `setup/` | `init.py`(team 초기화) · `sync.py`(solo 초기화·공용 파일 전파·뒤처짐 점검) · `modules.py`(공용/소유 표, 모듈 켜기) · `common/link_memory.py`(신원·메모리 링크·훅 경로) · `common/statusline.py` · `README.md`(기기별 설치) · `windows/bootstrap-prompt.md` |
| `profiles/solo/` | solo 프로필의 소유 파일 뼈대 (CLAUDE.md·BRAIN·STATE·settings·doc-keeper) |
| `.github/` | 이슈·PR 템플릿 (`/issue`와 같은 틀) |
| `optional/craft/` | **선택 모듈** — ArtCraft 디자인 앱 6종 MCP. team은 설치 스크립트 + 프로젝트 스킬 사본(윈도우 상대용, 전역 스킬 `craft`의 변형 — 전역이 바뀌면 diff 해서 맞춘다), solo는 `.mcp.json`·CLAUDE 절만(전역 스킬 사용) |
| `optional/film/` | **선택 모듈** — 영상 프로젝트 뼈대(`film/` 아래): `/update`·`tools/craft.sh`·폴더·영상용 BRAIN/STATE·`.mcp.json` 본. 옛 `film/_template` 흡수 |

## 전제

- 두 사람 모두 Claude Code + Git + Python 3.8+ (훅 스크립트가 표준 라이브러리만 쓴다). `/issue`를 쓰려면 GitHub CLI(`gh`) 로그인
- 기본 브랜치 `main`에 모두 직접 커밋(충돌 나면 `pull --rebase`). 남의 담당 영역·되돌리기 어려운 변경만 브랜치 + PR. 인원이 많아지면(4명 이상) PR 기본으로 바꾸는 쪽이 안전하다
- 응답·문서는 한국어 기준으로 쓰여 있다

## 이 템플릿 자체를 고칠 때

하네스를 쓰는 프로젝트에서 개선한 것(훅 수정, 커맨드 문구)은 여기로 되가져온다 — 공용 파일은 프로젝트에서 고치면 다음 sync 때 충돌로 잡히니, 처음부터 여기서 고쳐 커밋하고 `sync.py --all`. 프로젝트 고유값(이름·저장소 경로)은 넣지 않는다 — `grep -rn '{{' .`로 자리표시자가 남아 있는 게 정상인 저장소다. `sync.py`는 커밋 안 된 변경이 있으면 멈춘다(기준 커밋과 복사본이 어긋나지 않게).
