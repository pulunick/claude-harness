---
description: 세션 마무리 — 체크포인트(BRAIN/STATE) → 공유 메모리 → 커밋(작업자 트레일러) → 푸시. 항상 이 순서로 끝낸다
---

세션을 정해진 순서로 닫는다. 인자(있으면 커밋 요약 힌트): $ARGUMENTS

## 1. 체크포인트
`/checkpoint`의 절차대로 `.claude/BRAIN.md`(이번 세션에 **사용자가 확정한 것만**)와 `.claude/STATE.md`를 갱신한다. STATE "다음 작업" 맨 위는 **상대가 다음 세션에 바로 시작할 수 있게** 파일 경로까지 구체적으로. 완료 항목은 완료 로그로, 내가 잡았던 항목의 담당 표시를 정리한다. 두 파일의 "마지막 갱신" 날짜를 오늘로.

## 2. 공유 메모리
이번 세션에서 **두 사람 모두의 Claude가 알아야 할 새 사실**(작업 규칙·선호·도구 함정·외부 링크)이 생겼으면 `.claude/memory/`에 적는다 — 규약은 `.claude/memory/README.md`.
- 파일 하나에 사실 하나, 접두 `feedback_` / `project_` / `reference_`. 같은 주제가 이미 있으면 그 파일을 고친다(새로 만들지 않는다).
- `MEMORY.md` 색인에 한 줄 추가(색인에 없으면 죽은 메모리다).
- 개인 사정(내 PC 경로, 내 취향)은 `local_` 접두 → 커밋되지 않는다.
- 저장소가 이미 기록하는 것(코드 구조·git 이력·CLAUDE.md 규칙)은 넣지 않는다.

## 3. 커밋 전 점검
```bash
git pull --rebase --autostash      # 충돌 시 멈추고 보고. 강제 금지
python tools/harness/pending.py    # 맥은 python3. [PENDING] 목록 확인
python tools/harness/doctor.py     # 메모리 색인 1:1·STATE 담당 표기·날짜 등. FAIL 은 고치고 진행
git status --porcelain
```
`[UNKNOWN]`이면 "변경 없음"으로 취급하지 말고 사유를 보고한다. 하네스 자산(`.claude/**`·`tools/harness/**`·`.githooks/**`)을 고쳤으면 doctor 가 FAIL 0 인지 변경 전후로 대조한다 — 안전망을 고치는 작업일수록.

## 4. 스테이징 — 자동 스테이징 금지
`git add -A` / `git add .` 를 쓰지 않는다. **파일을 명시 나열**한다. 다음은 사용자가 명시 요청하지 않는 한 절대 올리지 않는다: `.mcp.json` · `.claude/settings.local.json` · `.claude/memory/local_*` · `local.properties` · `.env*` · `*.keystore` · `*.jks` · `img/candidates/` · 빌드 산출물. 스테이징 후 `git diff --cached --stat`을 보고하고, 파일명이 무해해 보여도 비밀값이 섞였는지 `git diff --cached`로 본다.

## 5. 커밋 메시지
```
<type>: <한 줄 요약>

<why 중심 1~2줄. what 은 diff 가 보여준다. STATE 항목을 가리킨다>

Worked-by: <who>@<machine>
```
- `type` ∈ `기능 | 수정 | 문서 | 하네스 | 에셋 | 설정 | 리팩터 | 체크포인트`
- `who`·`machine`은 `git config harness.who` / `git config harness.machine`에서 읽는다. **비어 있으면 커밋하지 말고** `python setup/common/link_memory.py`를 안내한다 — 이 트레일러가 "누가 어디서"의 근거다.
- `.githooks/prepare-commit-msg`가 `Worked-by`를 **자동으로 붙여 주고**, `pre-commit`이 금지 파일·비밀값·개인 절대경로를 막는다(`core.hooksPath` 설정된 기기). 훅이 막으면 `--no-verify`로 뚫지 말고 원인을 고친다.
- **트레일러는 마지막 문단 한 덩어리**여야 git이 인식한다. `Co-Authored-By:` 같은 다른 트레일러를 붙일 땐 `Worked-by:` **바로 다음 줄**에(사이에 빈 줄 금지). 커밋 후 `git log -1 --format='%(trailers:key=Worked-by)'`가 비어 있으면 `git commit --amend`로 고친다(푸시 전에만).
- 한국어. 개인 절대경로(`/Users/…`, `C:\…`)를 메시지·문서에 남기지 않는다 — 상대 기기에는 없는 경로다.
- 여러 성격이 섞였으면 커밋을 나눈다(예: 코드 1건 + `체크포인트:` 1건).

```bash
git commit -F - <<'MSG'
...
MSG
git push origin main
```
푸시가 거부되면 `git pull --rebase` 후 다시 푸시. `--force` / `--no-verify` / `reset --hard` 금지. 그래도 안 되면 보고하고 멈춘다.

## 6. 보고
```
## /wrap 완료 — <who>@<machine>
- BRAIN: <추가된 결정 n건 | 변경 없음>
- STATE: 다음 작업 1순위 = <한 줄>
- 메모리: <새 n건 / 갱신 n건 | 없음>
- 커밋: <sha> <type>: <요약>  (파일 n개)
- 푸시: origin/main ✅ | 실패 사유
- 상대에게 한마디: <다음 사람이 알아야 할 것 한 줄>
```
