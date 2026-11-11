---
name: feedback_dont_reload_users_tab
description: 사용자가 보고 있는 브라우저 탭은 새로고침·이동하지 않는다 — 확인은 새 탭이나 headless로
metadata:
  type: feedback
---

사용자가 직접 만지고 있는 웹 화면을 고친 뒤 확인할 때, 그 탭을 새로고침하거나 다른 주소로 보내지 않는다. 확인은 새 탭(또는 headless)을 따로 열어서 하고 끝나면 닫는다. 사용자에게는 "새로고침하면 적용돼요"라고 알리고, 저장하지 않은 작업이 있으면 새로고침으로 사라진다는 것도 같이 말한다.

**Why:** 화면에 저장 전 상태(편집 중인 값 등)가 있으면 새로고침 한 번에 사라진다. 2026-11-11 한 프로젝트에서 로컬 웹 화면을 고치며 사용자가 보던 탭을 여러 번 새로고침해, 저장 전 편집 상태가 지워졌을 수 있었다.
**How to apply:** 브라우저 도구로 화면을 고치고 확인하는 모든 작업. 탭이 하나뿐이어도 새 탭을 만든다. 관련: [[reference_browser_file_pitfalls]] [[feedback_test_without_writing_records]]
