# 프로젝트 "{{PROJECT_TITLE}}"

> 위치: 이 폴더. 저장소 `{{REPO}}`. 시작 {{DATE}}.
> {{DESCRIPTION}}
> 제품·스택·화면은 BRAIN.md에 확정되는 대로 채운다.

{{MEMBERS}} — 각자 기기에서 Claude Code로 같이 개발한다.

## 세션은 `/start`로 열고 `/wrap`으로 닫는다

| | 커맨드 | 하는 일 |
|---|---|---|
| 시작 | **`/start`** | `git pull` → 상황판(누가 어디서 마지막으로 무엇을 했나, 원격과의 차이, 메모리 링크) → BRAIN·STATE 읽기 → 오늘 할 일 제안 |
| 끝 | **`/wrap`** | 체크포인트(BRAIN/STATE) → 공유 메모리 → 명시 스테이징 → `Worked-by: 이름@기기` 트레일러로 커밋 → 푸시 → 보고 |

사용자가 "끝내자/마무리/정리해줘/커밋해줘"라고 하면 그게 곧 `/wrap`이다 — 순서를 건너뛰지 않는다. 세션 시작 훅이 `[하네스]` 블록을 찍어 주지만, **문서를 읽는 건 `/start`의 몫**이다: [.claude/BRAIN.md](.claude/BRAIN.md)(확정, 재논의 금지) → [.claude/STATE.md](.claude/STATE.md)(진행, 여기서 이어서). 처음 세션이면 [setup/README.md](setup/README.md)로 설치 상태를 점검한다.

## 운영 규칙 (BRAIN/STATE 하네스)

- 응답은 **한국어**.
- 결정 = BRAIN, 상태 = STATE, 중복 금지. 새 결정이 확정되면 BRAIN에(날짜·누가), 상태가 바뀌면 STATE에. 중간 저장은 `/checkpoint`, 세션 끝은 `/wrap`.
- BRAIN에 있는 결정과 충돌하는 제안을 하기 전에, BRAIN의 해당 항목을 근거로 사용자에게 먼저 확인.
- **여러 사람({{MEMBERS}})이 한 저장소에서 작업한다.** STATE "다음 작업"이 인수인계 통로다 — 항목마다 담당 {{MEMBER_TAGS}}를 적고, 남이 잡은 항목은 완료 보고 없이 지우지 않는다.
- **세션은 저장소 루트에서 연다.** 하위 폴더에서 열면 커맨드·메모리가 조용히 안 붙는다.

## 공유 메모리 (`.claude/memory/`)

- Claude의 자동 메모리 폴더(`~/.claude/projects/<경로인코딩>/memory`)를 각자 `setup/common/link_memory.py`로 이 폴더에 링크해 둔다. 그러면 **메모리 저장 = 커밋 대상**이 되어 `/wrap`으로 상대에게 간다.
- 접두 `feedback_`·`project_`·`reference_`는 공유(추적), `local_`은 개인(커밋 제외). 색인은 `MEMORY.md`, 규약은 [.claude/memory/README.md](.claude/memory/README.md).
- 링크가 안 된 기기에서는 `/start` 때 `MEMORY.md`를 직접 읽고, 새 메모리도 이 폴더에 직접 쓴다.

## 커밋 규칙 (누가 어디서 했는지 남긴다)

- 메시지: `<type>: <요약>` + 빈 줄 + why 1~2줄 + 빈 줄 + **`Worked-by: <이름>@<기기>`** (git config `harness.who`/`harness.machine`, `link_memory.py`가 설정). type ∈ `기능|수정|문서|하네스|에셋|설정|리팩터|체크포인트`.
- `git add -A`/`.` 금지 — 파일을 명시 나열. `.mcp.json`·`settings.local.json`·`local_*` 메모리·비밀키·`img/candidates/`는 올리지 않는다.
- `--force`·`--no-verify`·`reset --hard` 금지. 개인 절대경로를 메시지·문서·메모리에 남기지 않는다.
- 남의 작업은 `git log`의 `Worked-by`와 STATE 담당으로 본다. 세션 시작 훅이 최근 4커밋의 작업자를 보여준다.

## 협업 스타일

- 큰 방향은 사용자가 결정하되, **선택지 + 추천 하나**를 짧게 제시하면 빠르게 답한다. 질문은 꼭 필요한 것만.
- **기획을 먼저 확정하고 구현**으로 넘어간다. 아이디어가 툭 던져지면 원칙 검사 + 구체화 초안으로 정리해 주고, 결정엔 시기("MVP 이후" 등)를 붙인다.
- **비용 민감**: 유료 API·유료 생성은 디자인을 확정한 뒤 한 번에 몰아서. 개발 중 테스트는 가능한 한 로컬/무료 경로로.
- **사용자는 Claude가 Read로 본 이미지를 못 본다** → 미리보기·후보는 파일을 열어서(맥 `open`, 윈도우 `Start-Process`/`ii`) 사용자 화면에 띄우고, 여러 안은 비교 시트 한 장으로.
- 디자인 판정은 사용자가 보면서 빠르게 바꾼다 → **가장 최근 메시지를 따르고**, 교체된 후보도 지우지 말고 `img/candidates/`에 보관(로컬, 커밋 제외).
- 파일 이름 등 세부 지시는 정확히 따른다 (예: STATUS가 아니라 **STATE**).

## 상대에게 넘기기 — 이슈가 통로, PR은 선택

- **막힌 것·결정해 줄 것·부탁·"봐줘"는 GitHub 이슈**로: `/issue <내용>` → 종류 라벨(`버그|환경|결정|도움|검토|아이디어`) + 받을 사람을 assignee로 올린다(협업자가 한 명이면 자동, 여럿이면 `/issue @이름 <내용>` 또는 물어봄). 상대는 다음 `/start`의 상황판에서 "내게 온 이슈"로 본다. 처리하면 `/issue done #N <한 줄>`. 결정 이슈의 답은 BRAIN에도 적는다(이슈는 흘러가고 BRAIN이 정본).
- 웹·폰에서 올려도 된다 — 이슈 템플릿(`.github/ISSUE_TEMPLATE/`)이 같은 틀이다.
- STATE와의 경계: STATE = 계획과 담당, 이슈 = 지금 상대 손이 필요한 것. 이슈 때문에 내 작업이 멈추면 STATE 항목 뒤에 `→ #N 대기`.
- **PR은 선택**: 기본은 `main` 직접 커밋. 상대 담당 영역을 고치거나 되돌리기 어려운 변경이면 `이름/슬러그` 브랜치 + `gh pr create --assignee <상대>`, 받는 쪽이 Squash and merge. 절차는 `/issue` 커맨드 끝부분.
- `gh` CLI와 로그인이 필요하다(`setup/README.md`). 없으면 STATE "⏸ 결정 대기"에 적어 두는 걸로 대신한다.

## 반복 작업 (커맨드)

- `/start` · `/wrap` — 세션 열기/닫기 (위)
- `/issue` — 상대에게 넘기기 / 내게 온 것 보기 / 닫기 (위)
- `/checkpoint` — BRAIN/STATE만 갱신 (세션 중간 저장, `/wrap`이 내부에서 호출)
- `/mockup` — 화면 시안 HTML 빌드 + 아티팩트 재게시 (시안이 생기면 `docs/design/screen-mockup.html`)
- 점검 스크립트: `tools/harness/session_start.py`(상황판) · `tools/harness/pending.py`(미커밋 감지, Stop 훅이 30분에 한 번 알림) · `tools/harness/doctor.py`(설치·규약 점검)
- **하네스 공용 파일**(커맨드·훅·`tools/harness/`·`setup/common/` 등, 목록은 템플릿의 `setup/modules.py`)은 이 저장소에서 직접 고치지 않는다. 고칠 일이 생기면 템플릿 저장소에서 고쳐 커밋하고 `sync.py`로 받는다(`.claude/harness.json`이 기준 커밋, 뒤처지면 세션 시작 훅이 알림). 이 저장소 고유 파일(CLAUDE.md·BRAIN·STATE·settings·doc-keeper)은 여기서 관리.

## 저장소

- GitHub `{{REPO}}`, 브랜치 `main`. 모두 `main`에 직접 커밋(충돌 나면 `pull --rebase`, 강제 금지).
- 제외: `.mcp.json`(기기별 절대경로) · `.claude/settings.local.json` · `.claude/memory/local_*` · `img/candidates/` · 비밀키 파일(`local.properties`, `.env`) · 빌드 산출물
