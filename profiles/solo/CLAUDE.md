# 프로젝트 "{{PROJECT_TITLE}}" — {{DESCRIPTION}}

> 시작 {{DATE}}. 혼자 작업하는 프로젝트(claude-harness `solo` 프로필).

## 세션 시작 시 반드시

1. [.claude/BRAIN.md](.claude/BRAIN.md) 읽기 — 확정된 결정 (재논의 금지, 변경은 사용자 승인 필요)
2. [.claude/STATE.md](.claude/STATE.md) 읽기 — 진행 상태와 다음 작업 (여기서 이어서 시작)

## 운영 규칙 (BRAIN/STATE 하네스)

- 응답은 **한국어**.
- 결정 = BRAIN, 상태 = STATE, 중복 금지. 새 결정이 확정되면 BRAIN에(날짜), 상태가 바뀌면 STATE에. 세션 마무리나 요청 시 `/checkpoint`.
- BRAIN에 있는 결정과 충돌하는 제안은, BRAIN의 해당 항목을 근거로 사용자에게 먼저 확인.
- 큰 방향은 사용자가 결정하되 **선택지 + 추천 하나**를 짧게. 질문은 꼭 필요한 것만. 가장 최근 메시지를 따른다.
- 사용자는 Claude가 Read로 본 이미지를 못 본다 → 미리보기·후보는 `open`으로 띄우고, 여러 안은 비교 시트 한 장으로.
- 공통 절차는 전역 스킬: `craft`(크래프트 앱 MCP) · `codex-image`(그림 생성·크로마키) · `video-edit`(영상 편집). 여기엔 이 프로젝트 고유 사항만 적는다.

## 작업 체계 (하네스)

- 공용 파일(`.claude/commands/checkpoint.md`·`role.md`, `.claude/agents/doc-keeper.md`, 모듈 스크립트)은 **이 프로젝트에서 고치지 않는다**. 고칠 일이 생기면 하네스 저장소(`~/.claude/harness-home`이 가리키는 곳)에서 고쳐 커밋하고 `setup/sync.py --all`로 전파한다. 상태는 `.claude/harness.json`, 뒤처지면 세션 시작 훅이 알린다.
- 프로젝트 소유: 이 문서 · BRAIN · STATE · `.claude/settings.json` · `.mcp.json`.
- `/role` — 세션 역할. 기본 `normal`(한 세션이 전부, 간단한 작업). 구현과 검수를 나눌 땐 세션 둘을 열어 `/role coding`(review 문서 항목 구현·커밋·알림) + `/role review`(코드 안 고침, 검토·결정 기록·커밋 diff 대조) — 두 세션 체제(2026-10-28~).

## 이 프로젝트 고유

- 목적:
- 산출물·폴더:
