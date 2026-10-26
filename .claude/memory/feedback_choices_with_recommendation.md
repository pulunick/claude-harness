---
name: feedback_choices_with_recommendation
description: 결정이 필요하면 선택지 2~3개 + 추천 1개와 근거를 짧게 제시 — 큰 방향은 사용자가, 세부는 Claude가 진행
metadata:
  type: feedback
---

결정이 필요한 지점에서는 길게 설명하지 말고 **선택지 2~3개 + 추천 하나 + 한 줄 근거**로 묻는다. 결정에는 시기("MVP 이후" 등)를 붙여 준다. 사용자가 "진행해" 류로 맡기면 STATE 다음 작업을 알아서 이어간다.

**Why:** 이전 프로젝트들에서 검증된 방식. 기획을 먼저 확정하고 구현으로 넘어가는 순서를 쓰며, 선택지가 정리돼 있으면 빠르게 답한다. 질문이 많거나 설명이 길면 흐름이 끊긴다.

**How to apply:** AskUserQuestion을 쓸 때 추천 옵션을 첫 번째에 두고 "(추천)" 표시. 비용(유료 API·유료 생성)이 걸린 선택은 숫자를 같이 준다. 관련: [[feedback_latest_message_wins]]
