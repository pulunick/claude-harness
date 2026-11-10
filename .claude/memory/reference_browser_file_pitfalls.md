---
name: reference_browser_file_pitfalls
description: Claude in Chrome(웹 VS Code 키 입력·한글 파일명 업로드·--chrome 연결)과 윈도우에서 만든 한글 zip 풀기의 함정과 우회법
metadata:
  type: reference
---

**Claude in Chrome**
- 연결: 이어서 여는 세션은 `claude --continue --chrome`처럼 `--chrome`을 붙여야 Chrome 도구가 붙는다.
- 되돌릴 수 없는 제출(폼 전송·결제·게시) 직전에는 넣을 값을 표로 보여 주고 사용자 확인을 받는다. 비밀 값 입력과 로그인은 사용자가 한다.
- 웹 VS Code(code-server 등): 에디터에 포커스가 있을 때 computer 도구의 `key`/`type`을 쓰지 않는다 — `key "Page_Down"`이 키가 아니라 글자 `Page_Down`으로 입력된다(cmd+z로 복구). 스크롤은 미니맵 클릭이나 스크롤바 드래그로 하고, 파일 내용은 그 화면의 터미널에서 `sed -n`·`cat -A`로 확인하는 편이 안전하다.
- `file_upload`가 한글 파일명을 "only files this session is allowed to read"로 거부할 수 있다(특히 `sips` 등으로 새로 만든 파일 — NFC/NFD 정규화 차이로 추정). 영문 파일명 사본으로 올리면 된다.

**윈도우에서 만든 한글 zip**
- 파일명이 cp949로 저장돼 `unzip`·기본 `zipfile`에서 깨진다. Python 3.11+에서 `zipfile.ZipFile(path, metadata_encoding="cp949")`로 푼다(cp437→cp949 재인코딩 방식은 3.15에서 실패).
- 풀 때 `..`·절대경로가 든 항목은 건너뛴다(압축 밖으로 쓰기 차단).

**Evidence:** 2026-11-10 다른 프로젝트 세션 두 곳의 보고 — `--continue --chrome` 연결과 제출 전 확인, 웹 VS Code에서 `Page_Down`이 글자로 입력됨, 같은 폴더에서 새로 만든 한글 파일만 업로드 거부(영문 이름으로 바꾸자 통과), 윈도우 zip을 `metadata_encoding="cp949"`로 풀어 해결.
**How to apply:** Chrome으로 웹 에디터·업로드를 다루거나 받은 zip을 풀 때 먼저 본다. 새 사례가 나오면 이 파일에 덧붙인다.
