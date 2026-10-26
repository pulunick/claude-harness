## 크래프트 앱 (ArtCraft, MCP 연계)

- 6종(vectorcraft·photocraft·effectcraft·designcraft·filmcraft·soundcraft)을 **headless MCP**로 `.mcp.json`에 등록. 파일 접근은 이 프로젝트 폴더로 제한(filmcraft만 옵션이 없어 경로를 직접 프로젝트 안으로 지정).
- 설치·`.mcp.json` 생성은 `setup/windows/install-craft.ps1` / `setup/mac/install-craft.sh`. 공통 사용법·함정은 프로젝트 스킬 **`craft`**(`.claude/skills/craft/SKILL.md`, 맥·윈도우 차이 포함).
- 작업 폴더: 원본 `craft/{vector,photo,effect,design,film,sound}/`, 영상·PDF·오디오 결과물 `craft/out/`. 이미지 후보 `img/candidates/`(로컬), 확정 `img/`.
- 용도 예: 로고·아이콘(vector), 사진 보정·합성(photo), 영상 편집(film)·오디오(sound), 문서·PDF(design).
- 라이브 앱 브리지(`--control <port>`)를 쓰면 포트를 STATE에 적어 두 사람이 겹치지 않게 한다.
- 크래프트는 벡터·편집·모션·레이아웃용. **일러스트·사진 생성은 별도 도구** — 무엇을 쓸지는 BRAIN 6장에 확정될 때까지 미정.
