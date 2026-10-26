# claude-harness — 둘이서 Claude Code로 같이 만드는 프로젝트의 작업 체계

두 사람이 각자 기기(맥/윈도우)에서 Claude Code로 **같은 저장소**를 번갈아 작업할 때 필요한 것을 한 벌로 묶었다. 어떤 프로젝트든 이 템플릿으로 시작하면 첫 세션부터 다음이 된다.

- **세션 플로우 고정**: `/start`(pull → 상황판 → 문서 → 할 일) ~ `/wrap`(체크포인트 → 메모리 → 커밋 → 푸시)
- **문서 하네스**: `.claude/BRAIN.md`(확정된 결정만) / `.claude/STATE.md`(진행 상태, 담당 표시) — 인수인계는 이 두 파일로
- **누가 어디서 했는지**: 커밋마다 `Worked-by: 이름@기기` 트레일러 — git 훅이 자동으로 붙인다
- **공유 메모리**: Claude 메모리 폴더를 저장소 `.claude/memory/`에 링크 → 한 사람의 Claude가 배운 것이 커밋으로 상대에게 간다
- **규칙은 글보다 장치로**: 금지 파일·비밀값·개인 절대경로는 `pre-commit`이 막고, `git push --force`·`reset --hard`·`git add -A` 같은 명령은 Claude 훅(`pre_gate.py`)이 막는다. `doctor.py`가 설치·규약을 한 번에 점검
- **서로 넘기기**: `/issue` — 막힌 것·결정·부탁을 GitHub 이슈로 상대 담당 지정. PR은 선택
- 윈도우 상대방용 **부트스트랩 프롬프트**: Git·Claude Code만 사람이 깔고 나머지는 Claude가 셋업

## 새 프로젝트 시작 (3단계)

```bash
# 1. 이 템플릿으로 저장소 만들기 — GitHub "Use this template" 또는
gh repo create <owner>/<project> --private --template <owner>/claude-harness --clone
cd <project>

# 2. 자리표시자 채우기 (프로젝트명·GitHub 경로·두 사람 이름·기기). 인자 없이 실행하면 물어본다
python3 setup/init.py --project <project> --title "<한글 제목>" --owner <owner> \
    --person-a <나> --machine-a mac --person-b <상대> --machine-b win

# 3. 내 기기 신원 + 메모리 링크 + git 훅 활성화, 그리고 첫 커밋
python3 setup/common/link_memory.py --who <나> --machine mac
claude      # → /start
```

`init.py`가 하는 일: `{{PROJECT}}` 같은 자리표시자를 전부 치환하고, 프로젝트용 README로 바꾸고, 오늘 날짜를 BRAIN/STATE에 찍고, `/issue`용 라벨 6종을 만드는 `gh` 명령을 알려 준다(`--labels`를 주면 직접 만든다). 상대방에게는 `setup/windows/bootstrap-prompt.md`의 회색 박스를 메신저로 보내면 된다.

## 구성

| 경로 | 역할 |
|---|---|
| `CLAUDE.md` | 프로젝트 규칙 정본 (init 이 제목·이름을 채움). `AGENTS.md`는 다른 에이전트용 진입점 |
| `.claude/BRAIN.md` · `STATE.md` | 확정 / 진행. 뼈대만 있고 1~7장은 프로젝트가 채운다. 8장(작업 체계)은 이 하네스 설명 |
| `.claude/commands/` | `/start` `/wrap` `/checkpoint` `/issue` `/mockup` |
| `.claude/agents/doc-keeper.md` | BRAIN/STATE 갱신 전담 에이전트 |
| `.claude/settings.json` | 훅(SessionStart·Stop·PreToolUse) + 읽기 전용 명령 허용 목록. 기기별 `settings.local.json`은 커밋 안 함 |
| `.claude/memory/` | 공유 메모리. 규약은 안의 README. `feedback_*` 3건은 협업 스타일 기본값 — 안 맞으면 지운다 |
| `.githooks/` | `prepare-commit-msg`(트레일러) · `pre-commit`(금지 파일·비밀값·절대경로) |
| `tools/harness/` | `session_start.py`(상황판) · `pending.py`(미커밋 알림) · `pre_gate.py`(파괴적 명령 차단) · `doctor.py`(점검) |
| `setup/` | `init.py` · `common/link_memory.py`(신원·메모리 링크·훅 경로) · `common/statusline.py` · `README.md`(기기별 설치) · `windows/bootstrap-prompt.md` |
| `.github/` | 이슈·PR 템플릿 (`/issue`와 같은 틀) |
| `optional/craft/` | **선택 모듈** — ArtCraft 디자인 앱 6종을 headless MCP로 붙이는 설치 스크립트·스킬. `init.py --with-craft` 로 켠다 |

## 전제

- 두 사람 모두 Claude Code + Git + Python 3.8+ (훅 스크립트가 표준 라이브러리만 쓴다). `/issue`를 쓰려면 GitHub CLI(`gh`) 로그인
- 기본 브랜치 `main`에 둘 다 직접 커밋(충돌 나면 `pull --rebase`). 상대 담당 영역·되돌리기 어려운 변경만 브랜치 + PR
- 응답·문서는 한국어 기준으로 쓰여 있다

## 이 템플릿 자체를 고칠 때

하네스를 쓰는 프로젝트에서 개선한 것(훅 수정, 커맨드 문구)은 여기로 되가져온다. 프로젝트 고유값(이름·저장소 경로)은 넣지 않는다 — `grep -rn '{{' .`로 자리표시자가 남아 있는 게 정상인 저장소다.
