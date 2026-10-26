# 환경 설치 — 맥 · 윈도우

두 사람이 각자 기기에서 같은 작업 환경(Claude Code + BRAIN/STATE 하네스)을 갖추는 순서. 한 번만 하면 된다.

## 윈도우

> 빠른 길: 1·2번(Git, Claude Code 설치·로그인)과 GitHub 초대 수락만 사람이 하고, 나머지는 **[bootstrap-prompt.md](windows/bootstrap-prompt.md)** 를 Claude에게 붙여넣어 시킨다. 아래는 수동 전체 절차.

1. **Git for Windows** 설치 — https://git-scm.com/download/win (Claude Code가 bash를 여기서 빌려 쓴다). 설치 중 기본값 그대로.
2. **Claude Code** 설치 — PowerShell에서
   ```powershell
   irm https://claude.ai/install.ps1 | iex
   ```
   새 터미널을 열고 `claude` 실행 → 브라우저 로그인. 설치법이 바뀌었으면 https://docs.claude.com/ko/docs/claude-code/setup 기준.
3. **Python 3** — https://www.python.org/downloads/ ("Add python.exe to PATH" 체크) 또는 `winget install --id Python.Python.3.12`. 훅·점검 스크립트가 쓴다(표준 라이브러리만).
4. **저장소 클론** (경로에 한글·공백이 없는 곳 추천: 예 `C:\dev\{{PROJECT}}`)
   ```powershell
   git config --global http.sslBackend schannel    # 윈도우 SSL 인증서 오류 예방
   git clone https://github.com/{{REPO}}.git C:\dev\{{PROJECT}}
   cd C:\dev\{{PROJECT}}
   ```
   비공개 저장소면 GitHub 로그인이 뜬다(상대가 협업자로 추가해 둬야 함).
5. **신원 + 메모리 링크 + git 훅** —
   ```powershell
   python setup\common\link_memory.py --who <이름> --machine win
   ```
   커밋에 찍힐 이름·기기를 `git config harness.*`에 넣고, Claude 메모리 폴더를 저장소 `.claude\memory`에 정션으로 연결하고(두 사람의 Claude가 메모리 공유), `core.hooksPath`를 `.githooks`로 잡는다.
6. **GitHub CLI** — 이슈로 서로 넘기기(`/issue`)와 PR에 필요.
   ```powershell
   winget install --id GitHub.cli
   gh auth login        # GitHub.com → HTTPS → 브라우저 로그인
   ```
7. **Claude Code 시작** — 저장소 폴더에서 `claude`. 세션 시작 훅이 `[하네스]` 블록(내 신원·최근 커밋 작업자·메모리 링크 상태)을 찍는다. 첫 세션에서 할 말: **`/start`**. 세션을 끝낼 땐 **`/wrap`**.
8. (선택) **statusline** — 컨텍스트·사용량 막대. `setup/common/statusline.py`를 `C:\Users\<이름>\.claude\statusline.py`로 복사하고 `~/.claude/settings.json`에
   ```json
   "statusLine": { "type": "command", "command": "python C:/Users/<이름>/.claude/statusline.py" }
   ```
9. (선택) 크래프트 MCP — 프로젝트가 `optional/craft`를 켰다면 `Set-ExecutionPolicy -Scope Process Bypass; .\setup\windows\install-craft.ps1`. 안내는 `optional/craft/README.md`.

### 윈도우에서 다른 점 (Claude가 알아야 하는 것)
- Claude Code의 Bash 도구는 Git Bash로 돈다 → `open`은 없고 `start <파일>`(bash) / `ii <파일>`(PowerShell).
- 경로는 설정 JSON 안에서 `/`로 쓴다(`C:/dev/{{PROJECT}}`). `\`는 이스케이프 문제.
- PowerShell 5.1은 BOM 없는 UTF-8 스크립트의 한글을 깨뜨린다 → `.ps1`은 BOM 포함으로 저장. `Set-Content -Encoding UTF8`은 BOM을 붙이므로 JSON은 `[IO.File]::WriteAllText(..., UTF8Encoding $false)`로.
- 윈도우에는 실행 비트가 없다 → `gradlew` 같은 실행 파일을 윈도우에서 처음 커밋하면 맥에서 `Permission denied`. 맥 쪽에서 `git update-index --chmod=+x <파일>`.
- CLI 인자로 긴 텍스트(여러 줄)를 넘기면 줄바꿈이 잘릴 수 있다 — 파일로 넘긴다.
- iOS 빌드는 불가(맥 전용).

## 맥

1. Claude Code 설치(`curl -fsSL https://claude.ai/install.sh | bash`), `brew install gh && gh auth login`, python3는 기본 포함.
2. 저장소 클론 후
   ```bash
   python3 setup/common/link_memory.py --who <이름> --machine mac   # 신원 + 메모리 심링크 + git 훅
   python3 tools/harness/doctor.py                                   # FAIL 0 확인
   ```
3. `claude` 실행 → 시작 훅의 `[하네스]` 블록 확인 → `/start`.

## 둘이 같이 쓸 때 규칙

- 세션 시작: **`/start`**(pull → 상황판 → BRAIN/STATE). 세션 끝: **`/wrap`**(체크포인트 → 메모리 → 커밋 → 푸시). 자세한 커밋 규칙은 `CLAUDE.md` "커밋 규칙".
- 커밋마다 `Worked-by: 이름@기기` 트레일러가 붙는다 → `git log`만 봐도 누가 어느 기기에서 했는지 보인다. 세션 시작 훅이 최근 4건을 보여준다.
- 같은 파일을 동시에 고치지 않도록 STATE "다음 작업"에 담당을 적는다.
- 메모리는 `.claude/memory/`가 공유본(링크로 연결). `local_*.md`만 개인. 규약 `.claude/memory/README.md`.
- `.mcp.json`·`.claude/settings.local.json`은 커밋되지 않는다(기기별). 공용 설정은 `.claude/settings.json`(훅·권한).

## 문제가 생기면

먼저 `python tools/harness/doctor.py`(맥 `python3`) — 신원·훅·메모리 링크·색인·gh 를 한 번에 점검한다. FAIL 부터 고친다. 그래도 모르겠으면 `/issue`로 상대에게.

| 증상 | 확인 |
|---|---|
| 커밋이 "[hook] …" 으로 거부됨 | 금지 파일(`.mcp.json`·`local_*`·키)이나 비밀값·개인 절대경로가 섞임. 해당 파일을 `git restore --staged`, 내용 고친 뒤 다시. `--no-verify` 금지 |
| 시작 훅에 "메모리: 홈 링크 없음" | `python setup/common/link_memory.py --status`로 확인. 세션을 저장소 **루트**에서 열었는지(하위 폴더면 인코딩이 달라짐) |
| 커밋에 `Worked-by`가 없음 | `git config harness.who`가 비어 있음 → `link_memory.py` 재실행. `core.hooksPath`가 `.githooks`인지 |
| `/issue`가 assignee를 못 찾음 | 상대가 협업자 초대를 아직 수락 안 함. 라벨이 없으면 `python3 setup/init.py --labels` |
| 윈도우 `git clone`이 SSL 오류 | `git config --global http.sslBackend schannel` |
