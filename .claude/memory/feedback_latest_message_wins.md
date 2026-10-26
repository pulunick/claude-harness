---
name: feedback_latest_message_wins
description: 디자인·문구 판정은 사용자가 보면서 한 세션에 여러 번 바뀐다 — 가장 최근 메시지를 따르고, 교체된 후보는 지우지 말고 img/candidates/에 보관
metadata:
  type: feedback
---

디자인·문구 판정은 사용자가 결과를 보면서 빠르게 바꾼다(한 세션에 5번 바뀐 적 있음). 질문의 답과 직후 메시지가 다르면 **가장 최근 메시지**를 따른다. 바꿀 때마다 결과를 다시 띄워 확인받고, 교체된 후보는 지우지 말고 `img/candidates/`(커밋 제외)에 남긴다 — 되돌리자는 말이 자주 나온다.

**Evidence:** 이전 프로젝트에서 한 세션 안에 디자인 판정이 5번 바뀌었고, 되돌리자는 요청이 자주 나왔다.

**Why:** 이전 프로젝트의 이미지·연출 반복에서 굳어진 패턴.

**How to apply:** 바뀐 결정이 확정이면 BRAIN에 최종안만 적고, 거쳐 간 안은 적지 않는다. 관련: [[feedback_show_previews_to_user]]
