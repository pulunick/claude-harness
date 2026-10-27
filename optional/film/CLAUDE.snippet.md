## 영상 프로젝트 (film 모듈)

- 상위 `../CLAUDE.md`·`../README.md`(폴더 관례, 시리즈 규칙, 포트 배정표, 도구 업데이트)가 film 공통 규칙이고, 여기엔 이 프로젝트 고유 사항만 적는다. 편집 절차는 전역 스킬 `video-edit`, 앱 조작은 `craft`, 그림 생성은 `codex-image`.
- `media/원본/`은 어떤 경우에도 수정·삭제하지 않는다(접두어 `epNN_`, 시리즈는 `<시리즈>NN_`). 편집은 작은 단위로 → 보여주고 → 승인.
- 문서는 `docs/00_채널 · 01_회차(epNN_제목/) · 02_아이디어 · 03_편집`. 루트에 새 문서가 생기면 `docs/` 아래로 옮긴다(루트엔 CLAUDE.md만).
- 앱 열기: `tools/craft.sh film|effect|vector` — 포트는 `.mcp.json`의 `--bridge` 값을 읽는다. 포트를 바꾸면 `.mcp.json`과 `../README.md` 배정표만 고친다.
- `/update`: film 도구(크래프트 앱·CLI, HyperFrames, whisper.cpp, ffmpeg) 업데이트 확인·적용 (`../tools/`).
- 출력 규격: 가로 1920×1080 30fps | 세로 1080×1920 (택1)
- 자막: 폰트 · 크기 · 위치
- 이미지 생성: 후보 `edit/<종류>/candidates/` → 확정 `media/내보내기/이미지/<종류>/`, 프롬프트 기록 `edit/<종류>/prompts.md`
