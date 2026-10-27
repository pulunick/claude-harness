# BRAIN — 확정 사항 (프로젝트 "{{PROJECT_TITLE}}")

> **결정된 것만** 기록한다. 진행 상태는 [STATE.md](STATE.md), 갱신은 `/checkpoint`.
> 사용자가 승인한 것만 들어간다. 추측·미승인 제안·"하면 좋을 것"은 넣지 않는다. 각 결정에 날짜를 적는다.
> 마지막 갱신: {{DATE}} (초기화 — 뼈대)

## 1. 목적 (최우선 원칙)

- {{DESCRIPTION}} ({{DATE}})

## 2. 설계 원칙

- (미정) — 1차 판단 기준이 될 원칙 1~3개

## 3. 도구·스택

- 미정

## 4. 산출물·파일 규칙

- 미정

## 5. 작업 체계 ({{DATE}} — claude-harness solo 프로필)

- BRAIN(확정)/STATE(진행) 분리. 결정 = BRAIN, 상태 = STATE, 중복 금지. 세션 끝·요청 시 `/checkpoint`.
- 공용 파일은 하네스에서 고치고 `sync.py`로 받는다(`.claude/harness.json`). 응답 한국어, 선택지+추천, 비용 민감.
