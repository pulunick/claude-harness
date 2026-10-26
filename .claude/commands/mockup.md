---
description: 화면 시안(docs/design/screen-mockup.html) 수정 → 이미지 임베드 빌드 → 같은 아티팩트 URL로 재게시
---

화면 시안을 갱신하라. 요청 사항: $ARGUMENTS

절차:
1. `docs/design/screen-mockup.html`을 수정한다(없으면 새로 만든다). 디자인 토큰(팔레트·타입)은 `.claude/BRAIN.md` 4장을 따른다. 이미지 에셋은 `docs/design/assets/`에 900px 내외 JPEG로 압축해 넣고 HTML에서 `%%B64_<파일이름>%%` 토큰으로 참조한다.
2. 토큰을 썼다면 `python tools/build_mockup.py`로 base64 임베드 빌드 (최종 16MB 이하 확인). 빌드 결과는 `docs/design/screen-mockup.built.html`이며 커밋하지 않는다.
3. Artifact 도구로 **같은 파일 경로를 재게시**해 기존 URL을 유지한다. 첫 게시 후 URL을 `.claude/BRAIN.md` 4장과 CLAUDE.md "디자인 시안"에 적어 둔다. 다른 사람/세션에서 게시할 땐 그 URL을 `url` 파라미터로 전달한다.
4. 변경 요약과 링크를 사용자에게 보고한다.
