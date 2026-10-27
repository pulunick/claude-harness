## 크래프트 앱 (ArtCraft, MCP 연계)

- 6종(vectorcraft·photocraft·effectcraft·designcraft·filmcraft·soundcraft)을 `.mcp.json`에 등록. 기본은 headless + 이 폴더로 읽기/쓰기 루트 제한(filmcraft만 옵션이 없어 경로를 직접 프로젝트 안으로 지정). 라이브 앱 브리지(`--bridge <port>`)를 쓰면 포트가 다른 프로젝트와 겹치지 않게 적어 둔다.
- 공통 사용법·함정은 전역 스킬 **`craft`**(`~/.claude/skills/craft/SKILL.md`). 여기엔 이 프로젝트 고유 사항(용도·폴더·포트)만.
- 작업 폴더: 원본 `craft/{vector,photo,effect,design,film,sound}/`, 영상·PDF·오디오 결과물 `craft/out/`. 이미지 후보 `img/candidates/`(로컬), 확정 `img/`.
- 그림 생성(일러스트·캐릭터·배경)은 크래프트가 아니라 전역 스킬 **`codex-image`** — 후보/확정 폴더와 프롬프트 기록 위치는 위 폴더 규칙을 따른다.
