---
description: 상대에게 넘기기 — 문제·결정·부탁을 GitHub 이슈로 올려 상대 담당으로 지정(또는 내게 온 이슈 보기/닫기). 사용 `/issue <내용>` · `/issue list` · `/issue done #N <한 줄>`
---

멤버 사이의 "이거 네가 봐줘" 통로다. STATE는 계획, **이슈는 지금 막힌 것·결정해 줄 것·부탁**. 인자: $ARGUMENTS

## 공통: 나와 받을 사람 알아내기
```bash
gh auth status >/dev/null 2>&1 || echo "gh 로그인 필요: gh auth login"
ME=$(gh api user -q .login)
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
OTHERS=$(gh api "repos/$REPO/collaborators" -q '.[].login' | grep -v "^$ME$")
```
받을 사람(`OTHER`) 정하기: 인자가 `@이름`으로 시작하면 그 사람(GitHub 로그인 또는 CLAUDE.md의 멤버 이름 → 로그인 대응). 아니면 `OTHERS`가 **한 명**이면 자동, **여럿**이면 목록을 보여 주고 누구에게 넘길지 묻는다(결정·검토는 보통 그 영역 담당 — STATE `[이름]`을 보고 추천 하나를 붙인다). `OTHERS`가 비어 있으면(아직 협업자 추가 전) 담당 지정 없이 올리고 그 사실을 보고한다. `gh`가 없으면 설치 안내(`setup/README.md`)하고, 대신 STATE "⏸ 결정 대기"에 적어 둔다.

## `/issue [@이름] <내용>` — 올리기
1. 내용을 보고 **종류 라벨** 하나를 고른다: `버그`(동작이 틀림) · `환경`(설치·MCP·훅이 안 됨) · `결정`(상대가 정해야 진행됨) · `도움`(상대 기기·권한·지식이 필요) · `검토`(코드/디자인 봐줘) · `아이디어`.
2. 제목: `<종류>: <한 줄>`. 본문은 아래 틀을 채운다 — **상대 기기에서 재현·판단할 수 있게**, 추측과 사실을 나눈다.
   ```
   ## 무엇이 / 뭘 원하나
   (한 문단. 결정이면 선택지 + 내 추천)

   ## 해본 것 / 확인한 것
   - 명령·출력 요약(오류 문구는 그대로). 비밀값·개인 절대경로는 빼고 <repo>/… 로

   ## 재현 / 관련 파일
   - 파일 경로, 커밋 sha, STATE 항목

   ## 급한가
   (막혀서 못 하는 중 / 다음 세션까지 / 언제든)

   Worked-by: <who>@<machine>  ← git config harness.who/machine
   ```
3. 생성:
   ```bash
   gh issue create --title "<제목>" --label "<종류>" ${OTHER:+--assignee "$OTHER"} --body-file <임시파일>
   ```
   본문은 heredoc으로 임시 파일에 쓴 뒤 넘긴다(여러 줄·따옴표 안전).
4. 막혀서 내 작업이 멈춘 거면 STATE 해당 항목 뒤에 `→ #N 대기`를 적는다(커밋은 `/wrap`에서).
5. 보고: 이슈 URL + 담당 + "담당자의 다음 `/start`에서 보임".

## `/issue list` — 내게 온 것 / 내가 올린 것
```bash
gh issue list --assignee @me --state open
gh issue list --author @me --state open
```
내게 온 것은 급한 순으로 1~3줄 요약하고 어느 것부터 볼지 묻는다.

## `/issue done #N <한 줄>` — 처리 후 닫기
처리 내용(무엇을 고쳤는지, 커밋 sha, 올린 사람이 할 일이 남았는지)을 코멘트로 남기고 닫는다. 올린 사람이 확인해야 끝나는 거면 닫지 말고 코멘트 + `--add-assignee`로 되넘긴다(`OTHER` = 이슈 작성자 `gh issue view N --json author -q .author.login`).
```bash
gh issue close N --comment "<처리 내용 · 커밋 sha · 남은 일>"
# 되넘기기: gh issue comment N --body "..." && gh issue edit N --add-assignee "$OTHER" --remove-assignee "$ME"
```

## `/issue reply #N <내용>` — 질문·중간 보고
`gh issue comment N --body "..."`. 결정 이슈에 답할 땐 **결정 내용을 BRAIN에도** 적는다(이슈는 흘러가고 BRAIN이 정본).

## 코드 검토를 받고 싶을 때 (선택 — PR)
기본은 `main` 직접 커밋이다. 다음일 때만 브랜치 + PR:
- 상대 담당(STATE `[이름]`) 영역을 내가 고쳐야 할 때
- 되돌리기 어려운 변경(스키마·빌드 설정)이라 눈 하나 더 거치고 싶을 때
```bash
git switch -c <who>/<slug>          # 예: 하늘/offline-map
# … 커밋은 /wrap 규칙 그대로(Worked-by 트레일러) …
git push -u origin <who>/<slug>
gh pr create --fill --assignee "$OTHER" --label 검토
```
받은 사람은 보고 **`gh pr merge N --squash --delete-branch`**(또는 웹에서 Squash and merge). 문제 있으면 PR 코멘트로 되돌려준다. 리베이스·강제 푸시는 하지 않는다.
