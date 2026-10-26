# 윈도우 부트스트랩 — Claude에게 붙여넣는 프롬프트

사람이 직접 할 것은 **Git for Windows 설치 → Claude Code 설치·로그인 → GitHub 초대 수락** 뿐이다. 그 뒤는 `C:\dev` 같은 빈 폴더에서 `claude`를 열고 아래를 통째로 붙여넣는다. (저장소 밖에서 여는 세션이라 CLAUDE.md가 아직 없으므로 지시를 다 적어 둔다.)

> **링크가 아니라 내용을 보낸다.** 저장소가 비공개면 상대 Claude는 이 페이지를 못 읽는다 — 보내는 쪽이 아래 회색 박스를 복사해 메신저로 전달한다. 설치 폴더는 아무 데나 괜찮다 — 스크립트가 자기 위치 기준으로 경로를 잡는다. 멤버가 여럿이면 4번의 이름·기기만 그 사람 것으로 바꿔 보낸다.
>
> **윈도우 git SSL 오류**(`SSL certificate problem` / `CAfile` 류)가 나면 먼저 `git config --global http.sslBackend schannel` — 윈도우 인증서 저장소를 쓰게 한다.

```
너는 내 윈도우 PC에 개발 환경을 셋업해 주는 중이야. 한국어로, 단계마다 뭘 했는지 한 줄씩 보고하고, 실패하면 멈추고 알려줘. 비밀번호·토큰은 절대 파일에 쓰지 마.

1. 사전 확인: git --version, python --version, gh --version, winget --version 을 확인해. 없는 것만 설치해:
   - python 없으면: winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements
   - gh 없으면:     winget install --id GitHub.cli -e --accept-package-agreements --accept-source-agreements
   설치했으면 새 셸에서만 PATH가 잡히니, 이후 명령은 전체 경로로 찾거나(where.exe python) 나한테 "터미널 다시 열고 다시 붙여넣어" 라고 말해.
2. gh auth status 가 로그인 안 됨이면 멈추고 나한테 `gh auth login` 을 직접 치라고 안내해 (GitHub.com → HTTPS → 브라우저). 끝나면 계속.
3. 저장소 클론: 먼저 git config --global http.sslBackend schannel (윈도우 SSL 오류 예방). 그 다음 git clone https://github.com/{{REPO}}.git C:\dev\{{PROJECT}}  (폴더는 내가 다르게 정했으면 그걸로, 이미 있으면 그 안에서 git pull). 로그인 창(Git Credential Manager)이 뜨면 멈추고 나한테 GitHub 로그인하라고 알려줘.
4. C:\dev\{{PROJECT}} 에서 실행: python setup\common\link_memory.py --who {{PERSON_B}} --machine {{MACHINE_B}}
   - 커밋 신원, Claude 메모리 폴더 → 저장소 .claude\memory 정션, git 훅 경로를 잡는다.
   - setup\windows\install-craft.ps1 이 있으면(프로젝트가 크래프트 MCP를 쓰면) PowerShell로: Set-ExecutionPolicy -Scope Process Bypass; .\setup\windows\install-craft.ps1  — 앱 6종(약 800MB)을 받으니 기다려.
5. 검증: python tools\harness\doctor.py 를 돌려 FAIL 이 0인지 확인하고 결과를 보여줘. WARN 은 내용만 알려줘.
   그리고 그 결과를 상대가 볼 수 있게 이슈로 올려: gh issue create -R {{REPO}} --title "환경: {{PERSON_B}} 윈도우 셋업 보고" --label 환경 --assignee {{OWNER}} --body-file <doctor 출력을 저장한 임시파일>  (실패했어도 올려 — 그게 도움 요청이다)
6. 마지막으로 이렇게 안내해: "이 창을 닫고, C:\dev\{{PROJECT}} 폴더에서 claude 를 다시 열어 /start 라고 치세요."
```

## 왜 이 순서인가
- Claude Code 자체와 Git은 Claude가 깔 수 없다(자기가 돌 발판이라).
- 저장소 밖에서 연 세션은 CLAUDE.md·커맨드·훅이 없다 → 셋업만 시키고, 끝나면 **저장소 안에서 다시 연다**. 메모리 링크도 저장소 루트 경로 기준이라 이 재시작이 필수다.
- `gh auth login`은 브라우저 상호작용이라 사람이 친다.
