---
description: film 도구(크래프트 앱·CLI, HyperFrames, whisper.cpp, ffmpeg) 업데이트를 확인하고 검증하며 적용한다
---

영상 도구 업데이트를 적용하라. 스크립트는 `../tools/`(film/tools)에 있다. $ARGUMENTS

1. `../tools/update-check.sh --force`를 실행하고 `../.updates/report.md`를 읽는다. 업데이트가 없으면 그렇게 보고하고 끝.
2. 항목별로 **릴리스 노트 발췌를 읽고** 우리 워크플로(전사 `transcript.set`, `graphics.newFromFile`, 캡션 명령, HyperFrames 알파 렌더·변수)에 영향이 있는지 한 줄씩 판단해 사용자에게 보여준다. 깨질 가능성이 있는 항목은 이유를 적고 사용자 확인을 받는다.
3. 적용 순서:
   - brew(whisper.cpp, ffmpeg): `../tools/update-apply.sh brew <formula>`
   - HyperFrames: `../tools/update-apply.sh plugin` → `../tools/update-apply.sh hyperframes <최신>` (템플릿 lint/check/렌더 회귀가 자동으로 돌고, 실패하면 핀이 되돌아간다). 실패하면 릴리스 노트에서 원인을 찾아 템플릿을 고치거나 핀을 유지한다.
   - 크래프트 앱: 사용자에게 **ArtCraft Launcher ▸ Check for Updates**를 눌러 달라고 한 뒤(앱 교체는 GUI만 가능), `../tools/update-apply.sh cli <app>`로 CLI를 앱과 같은 버전으로 맞춘다. 그다음 `<app>-cli commands`로 우리가 쓰는 명령이 남아 있는지, FilmCraft는 `filmcraft-cli exec transcript.models`로 전사가 켜졌는지(`available`) 확인한다.
4. 적용 결과를 `../.updates/report.md` 끝에 "적용 로그 YYYY-MM-DD"로 추가하고, 프로젝트 STATE.md 완료 로그에 한 줄 남긴다. 새로 알게 된 함정은 전역 스킬(`craft` 또는 `video-edit`)에, 프로젝트 고유 변화는 CLAUDE.md에 적는다.
5. 바뀐 기능이 우리 파이프라인을 더 좋게 만들 수 있으면(예: FilmCraft 전사 복귀, HyperFrames 새 캡션 기능) 기획서 `docs/03_편집/`에 "적용 후보"로 한 줄 적는다.
