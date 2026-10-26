# STATE — 진행 상태 (프로젝트 "{{PROJECT_TITLE}}")

> 지금 하고 있는 것 / 다음 것 / 보류된 것. **확정된 결정은 여기 두지 말고 [BRAIN.md](BRAIN.md)로 옮긴다.** 갱신은 `/checkpoint`.
> 여러 사람이 쓰므로 항목 앞에 담당을 적는다: {{MEMBER_TAGS}}.
> 마지막 갱신: {{DATE}} (저장소 생성 — claude-harness 템플릿으로 초기화)

## ▶ 다음 작업 (여기서 시작)

### 0. 환경 준비
- [ ] `[{{PERSON_A}}]` 나머지 멤버를 협업자로 초대(write) — `gh repo add-collaborator` 또는 웹. 수락하면 `/issue` assignee 자동 인식
- [ ] `[{{PERSON_A}}]` `/issue`용 라벨 6종 생성 — `python3 setup/init.py --labels` 또는 init 이 출력한 `gh label create` 명령
- [ ] `[{{PERSON_B}}]` (멤버마다 한 줄씩) {{MACHINE_B}} 셋업 — `setup/README.md` 순서대로: Git·Claude Code 설치 → 클론 → `python setup/common/link_memory.py`(이름·기기 신원 + 메모리 링크 + git 훅) → `claude` → 시작 훅 `[하네스]` 블록에 "메모리: 연결됨" 확인 → `/start`. 막히는 부분은 여기 적어 두기
- [ ] `[{{PERSON_B}}]` (멤버마다) 첫 `/wrap`으로 커밋 한 번 — `git log`에 `Worked-by: {{PERSON_B}}@{{MACHINE_B}}`가 찍히는지 확인
- [ ] `[누구나]` 각자 statusline 설정(선택) — `setup/common/claude-settings.example.json` 참고

### 1. 기획 (BRAIN 1~2장 채우기) — 구현보다 먼저
- [ ] `[누구나]` 제품이 해결할 것 3개 이내로 좁히기 → `docs/planning.md`
- [ ] `[누구나]` 설계 원칙 1~3개 (BRAIN 2장)

### 2. 스택 결정 (BRAIN 3장)
- [ ] `[누구나]` 플랫폼·프레임워크·저장 방식

## ⏸ 결정 대기 (사용자 답 필요)
- 프로젝트 이름(`{{PROJECT}}`은 임시인지)

## 🔶 보류
- (없음)

## ✅ 완료 로그
- {{DATE}} `[{{PERSON_A}}@{{MACHINE_A}}]` 저장소 `{{REPO}}` 생성, claude-harness 템플릿으로 초기화
