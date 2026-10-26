# optional/craft — ArtCraft 디자인 앱 6종을 headless MCP로

VectorCraft·PhotoCraft·EffectCraft·DesignCraft·FilmCraft·SoundCraft(https://getartcraft.com, 오픈소스 storytold/*)를 Claude Code MCP 서버로 붙인다. 로고·아이콘(vector), 사진 보정·합성(photo), 모션·타이틀(effect), 레이아웃·PDF(design), 영상 편집(film), 오디오(sound)를 Claude가 직접 다룰 수 있다. **그림·사진 생성은 포함되지 않는다**(별도 도구).

## 켜기

```bash
python3 setup/init.py --with-craft      # 초기화 때. 이미 초기화한 저장소에서 실행해도 이 모듈만 켜진다
```

하는 일: `setup/mac/install-craft.sh`·`setup/windows/install-craft.ps1` 복사, 프로젝트 스킬 `.claude/skills/craft/` 복사, `CLAUDE.md`에 "크래프트 앱" 절 추가(`CLAUDE.snippet.md`), `.claude/settings.json`의 `enabledMcpjsonServers`에 6종 등록, `craft/{vector,photo,effect,design,film,sound,out}/` 작업 폴더와 `.gitignore` 항목.

## 각 기기에서

- 맥: `bash setup/mac/install-craft.sh` (GUI 앱이 이미 있으면 `--mcp-only`). CLI를 최신으로 맞추려면 `--force`
- 윈도우: `Set-ExecutionPolicy -Scope Process Bypass; .\setup\windows\install-craft.ps1` — 관리자 권한 없이 `%LOCALAPPDATA%\ArtCraft\`에 portable 설치, 약 800MB
- 둘 다 끝에 `.mcp.json`을 **기기 절대경로**로 생성한다(커밋 제외). 파일 접근은 저장소 폴더로 제한
- `claude` 실행 → MCP 승인 → `/mcp`에서 6종 connected 확인. `doctor.py`가 `.mcp.json`의 CLI 경로를 점검한다

## 사용법·함정

프로젝트 스킬 **`craft`**(`.claude/skills/craft/SKILL.md`) — 공통 흐름, 맥·윈도우 차이(폰트 등), 앱별 함정. 라이브 앱 브리지(`--control <port>`)를 쓰면 포트를 STATE에 적어 두 사람이 겹치지 않게 한다.
