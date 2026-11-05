---
name: feedback_zsh_no_word_splitting
description: 맥 기본 셸 zsh는 변수에 담은 명령 옵션을 공백으로 나누지 않는다 — $OPTS 로 넘긴 ffmpeg 옵션이 통째로 한 인자가 되어 조용히 실패
metadata:
  type: feedback
---

Bash 도구는 맥에서 **zsh**로 돈다. zsh는 bash와 달리 따옴표 없는 변수도 공백으로 쪼개지 않는다(`SH_WORD_SPLIT` 꺼짐). 그래서 `V="-c:v libx264 -crf 14"; ffmpeg -i a.mp4 $V b.mp4` 는 옵션 전체가 한 인자로 넘어가 실패한다. 여러 명령을 `;`로 이은 묶음에서는 실패가 묻혀 다음 단계로 넘어간다. 옵션 묶음은 **셸 함수**(`enc(){ ffmpeg -i "$1" -c:v libx264 -crf 14 "$2"; }`)나 배열(`opts=(-c:v libx264 -crf 14); ffmpeg ... "${opts[@]}"`)로 쓰고, 묶음 실행 뒤에는 결과 파일이 실제로 생겼는지 확인한다.

**Evidence:** 2026-11-05 pb_ai_video 세션 — `V="-c:v libx264 -crf 14 -pix_fmt yuv420p -vf scale=..."` 를 `ffmpeg ... $V out.mp4` 로 3번 썼더니 셋 다 "At least one output file must be specified" 로 실패했고, 같은 묶음의 `set -e` 도 zsh 에서 멈추지 않아 뒤 단계가 없는 파일을 찾다 실패했다. 셸 함수로 바꾸자 정상.
**Why:** 맥과 리눅스·Git Bash(bash)에서 같은 명령이 다르게 동작한다 — 윈도우 상대방(Git Bash)에서 되던 스크립트가 맥에서 조용히 깨질 수 있다.
**How to apply:** 셸 한 줄에서 옵션을 변수로 재사용하지 않는다. 필요하면 함수·배열을 쓰거나 파이썬 스크립트로 옮긴다. 결과 파일 존재·길이를 마지막에 확인한다.
