---
name: feedback_show_previews_to_user
description: 사용자는 Claude가 Read로 본 이미지를 못 본다 — 후보·렌더·시안은 파일을 열어 사용자 화면에 띄우고, 여러 안은 비교 시트 한 장으로
metadata:
  type: feedback
---

이미지·렌더·시안을 만들었으면 반드시 **사용자 화면에 띄운다**: 맥 `open <파일>`, 윈도우 `start <파일>`(Git Bash) / `ii <파일>`(PowerShell). 여러 후보(A/B/C)는 Pillow 등으로 비교 시트 한 장을 만들어 보여주고 [[feedback_choices_with_recommendation]] 방식으로 묻는다.

**Why:** 이전 프로젝트에서 확인 — Claude가 Read로 본 이미지는 대화에 보이지 않아, 사용자는 "뭘 보고 판단하라는 건지" 모른 채 설명만 받게 된다.

**How to apply:** 크래프트 `render_preview`·`export` 결과, 생성 이미지 후보, 목업 빌드 결과 모두 해당. MP4가 "안 보인다"고 하면 플레이어가 같은 파일명의 옛 창을 쥐고 있는 경우가 많다 — 프레임을 뽑거나 GIF로 브라우저에서 보여준다.
