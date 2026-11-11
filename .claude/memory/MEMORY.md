# Memory Index — {{PROJECT}} (공유)

> 이 폴더는 저장소가 관리한다(`.claude/memory/`, 규약은 [README](README.md)). 개인 전용은 `local_*.md`(커밋 제외).

- [선택지 + 추천 하나로 묻기](feedback_choices_with_recommendation.md) — 큰 방향은 사용자가 정하되 질문은 짧게, 추천 1개 + 근거
- [미리보기는 사용자 화면에 띄우기](feedback_show_previews_to_user.md) — 사용자는 Claude가 Read로 본 이미지를 못 본다, 여러 안은 비교 시트
- [가장 최근 메시지를 따른다](feedback_latest_message_wins.md) — 디자인 판정은 보면서 빠르게 바뀜, 교체분은 candidates에 보관
- [zsh는 변수 옵션을 쪼개지 않음](feedback_zsh_no_word_splitting.md) — `$OPTS` 로 넘긴 ffmpeg 옵션이 한 인자가 되어 조용히 실패, 함수·배열 사용 + 결과 파일 확인
- [브라우저·파일 함정](reference_browser_file_pitfalls.md) — Chrome: `--chrome`으로 연결, 웹 VS Code에선 key 금지, 한글 파일명 업로드 거부 → 영문 사본 · 윈도우 한글 zip은 `metadata_encoding="cp949"`
- [사용자가 보는 탭은 새로고침하지 않기](feedback_dont_reload_users_tab.md) — 확인은 새 탭·headless, 사용자에겐 "새로고침하면 적용"과 저장 전 작업 유실을 알림
- [지울 수 없는 기록에 남는 버튼은 시험으로 누르지 않기](feedback_test_without_writing_records.md) — 복사본+다른 포트 또는 화면 안 임시 상태로 확인, 안 눌러 본 것은 보고에
