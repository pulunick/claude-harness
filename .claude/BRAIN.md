# BRAIN — 확정 사항 (프로젝트 "{{PROJECT_TITLE}}")

> **결정된 것만** 기록한다. 진행 상태는 [STATE.md](STATE.md), 갱신은 `/checkpoint`.
> 사용자가 승인한 것만 들어간다. 추측·미승인 제안·"하면 좋을 것"은 넣지 않는다. 각 결정에 날짜와 누가 정했는지 적는다.
> 마지막 갱신: {{DATE}} (초기화 — 뼈대, 8장 작업 체계)

## 1. 제품 정의

- **무엇**: {{DESCRIPTION}} ({{DATE}}, {{PERSON_A}})
- 이름: 미정
- 핵심 기능: 미정 — 후보 논의는 STATE "결정 대기"에

## 2. 설계 원칙

- (미정) — 이 제품의 1차 판단 기준이 될 원칙 1~3개

## 3. 기술 스택

- 미정. 결정 시 함께 적을 것: 플랫폼, 프레임워크, 저장(DB), 외부 의존성·제약

## 4. 화면 · 디자인

- 미정. 팔레트·타입은 정해지면 여기에, 시안은 `docs/design/screen-mockup.html` + 아티팩트 URL

## 5. 데이터

- 미정 (스키마는 `docs/db-schema.md`에)

## 6. 에셋

- 미정 (생성 도구, 파일 규칙 `img/`·`img/candidates/`)

## 7. 배포

- 미정

## 8. 작업 체계 ({{DATE}}, {{PERSON_A}} — claude-harness 템플릿)

- 문서 하네스: BRAIN(확정)/STATE(진행) 분리. 결정 = BRAIN, 상태 = STATE, 중복 금지. STATE 항목에 담당 {{MEMBER_TAGS}}
- **세션 플로우 고정**: `/start`(pull → 상황판 → BRAIN/STATE → 할 일) ~ `/wrap`(체크포인트 → 공유 메모리 → 명시 스테이징 커밋 → 푸시). "마무리/커밋해줘" = `/wrap`
- **공유 메모리**: `.claude/memory/`를 저장소에 두고 각자 Claude 메모리 폴더를 링크(`setup/common/link_memory.py`). `feedback_/project_/reference_` 공유, `local_` 개인
- **커밋 규칙**: `<type>: 요약` + why + `Worked-by: 이름@기기` 트레일러(git config `harness.who/machine`). 자동 스테이징·강제 푸시·개인 절대경로 금지
- **규칙은 글보다 장치로**: 트레일러는 `.githooks/prepare-commit-msg`가 붙이고, 금지 파일·비밀값·개인 절대경로는 `pre-commit`이 막고, 파괴적 git 명령은 Claude 훅 `pre_gate.py`가 막는다. 줄바꿈은 `.gitattributes`로 LF 통일. 점검은 `tools/harness/doctor.py`
- **서로 넘기기 = GitHub 이슈**(`/issue`, 종류 라벨 + 상대 assignee, 양방향). **PR은 선택** — 상대 담당 영역·되돌리기 어려운 변경만 브랜치+PR, 받는 쪽이 Squash merge
- 멤버 {{MEMBERS}}가 Claude Code로 같은 저장소 `main`에서 작업. 기기별 설정(`.mcp.json`, `settings.local.json`)은 커밋하지 않는다
- 응답 한국어, 선택지+추천 방식, 비용 민감(유료 생성은 확정 후 일괄)
