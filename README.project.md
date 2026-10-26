# {{PROJECT}} — {{PROJECT_TITLE}}

{{DESCRIPTION}}

{{PERSON_A}}({{MACHINE_A}})·{{PERSON_B}}({{MACHINE_B}}) 두 사람이 각자 기기에서 Claude Code로 같이 만든다. 규칙 정본은 [CLAUDE.md](CLAUDE.md), 확정 사항은 [.claude/BRAIN.md](.claude/BRAIN.md), 진행 상태는 [.claude/STATE.md](.claude/STATE.md).

## 시작하기

- 설치: [setup/README.md](setup/README.md) (맥·윈도우). 윈도우 상대방은 [setup/windows/bootstrap-prompt.md](setup/windows/bootstrap-prompt.md)의 회색 박스를 Claude에게 붙여넣으면 된다
- 세션: 저장소 루트에서 `claude` → **`/start`**. 끝낼 땐 **`/wrap`**
- 상대에게 넘길 것: `/issue <내용>`

## 작업 체계

[claude-harness](https://github.com/{{OWNER}}/claude-harness) 템플릿에서 시작했다 — 세션 플로우·BRAIN/STATE·`Worked-by` 트레일러·공유 메모리·git 훅·점검 스크립트. 하네스를 고쳤으면 템플릿 저장소에도 되가져간다.
