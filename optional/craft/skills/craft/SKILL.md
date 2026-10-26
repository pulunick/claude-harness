---
name: craft
description: ArtCraft 크래프트 앱(VectorCraft·PhotoCraft·EffectCraft·DesignCraft·FilmCraft·SoundCraft) MCP 공통 사용법·함정·작업 흐름(맥·윈도우). 로고·아이콘·벡터 그래픽, 이미지 편집·합성, 모션·타이틀 렌더, 레이아웃·PDF, 영상 편집, 오디오 믹스를 크래프트 MCP 도구(mcp__vectorcraft__* 등)로 할 때, 또는 크래프트 MCP 연결이 안 될 때 먼저 읽는다. 프로젝트별 연결·폴더·용도는 CLAUDE.md "크래프트" 절이 우선.
---

# 크래프트 앱 공통 가이드 (맥 · 윈도우)

ArtCraft(storytold) 앱 6종. 각 앱의 **CLI `mcp` 서브커맨드가 stdio MCP 서버**다. 이 프로젝트는 `setup/` 스크립트가 설치하고 `.mcp.json`을 만들어 준다.

| 앱 | 급 | 주 용도 | CLI 이름 |
|---|---|---|---|
| VectorCraft | Illustrator | 로고·워드마크·UI 아이콘·앱 아이콘 → SVG/PNG | `vectorcraft-cli` |
| PhotoCraft | Photoshop | 사진 보정·크롭·레이어 합성·누끼 보조 | `photocraft-cli` |
| EffectCraft | After Effects | 로고 모션·타이틀·홍보 모션 → MP4/PNG 시퀀스 | `effectcraft-cli` |
| DesignCraft | InDesign | 일정표·기획서·원페이저 → PDF/PNG | `designcraft-cli` |
| FilmCraft | Premiere | 컷 편집·자막·여행 영상 → MP4 | `filmcraft-cli` |
| SoundCraft | Pro Tools | 효과음·배경음 다듬기, 영상 오디오 믹스 → WAV | `soundcraft-cli` |

그림 자체(일러스트·캐릭터·사진 생성)는 크래프트가 아니라 이미지 생성 도구 몫. 크래프트는 벡터·편집·모션·레이아웃.

## 설치 위치 (OS별)

| | 맥 | 윈도우 |
|---|---|---|
| GUI 앱 | `/Applications/<App>.app` (getartcraft.com 런처 또는 dmg) | portable: `%LOCALAPPDATA%\ArtCraft\<app>\<app>.exe` · MSI: `C:\Program Files\<App>\<app>.exe` |
| CLI | `~/.local/bin/<app>-cli` (릴리스의 `<app>-cli-<ver>-macos-universal.zip`) | **GUI와 같은 폴더의 `<app>-cli.exe`** (portable zip·MSI 둘 다 포함, PATH엔 없음) |
| 설치 스크립트 | `setup/mac/install-craft.sh` | `setup/windows/install-craft.ps1` |
| 파일 열어 보여주기 | `open <파일>` | `Start-Process <파일>` (= `ii`) |
| 한글 폰트 | `Apple SD Gothic Neo` | `Malgun Gothic` |

윈도우 릴리스에는 CLI 단독 zip이 없다 — 앱 zip/MSI 안에 `<app>-cli.exe`가 같이 들어 있다(2026-10-25 확인, vectorcraft 0.16.0 portable). 업데이트는 앱 폴더를 새 zip으로 통째 교체.

## 연결 방식 (프로젝트가 고름)

- **headless** (이 프로젝트 기본): `<cli> mcp --automation-read-root <폴더> --automation-write-root <폴더>` — 창 없이 엔진만, 파일 접근을 그 폴더로 제한
- **bridge(앱 연결)**: 앱을 `--control <port>`로 띄우고(맥 `open -a <App> --args --control 7979`, 윈도우 `& "<app>.exe" --control 7979`) MCP를 `<cli> mcp --connect 127.0.0.1:<port>`로 붙임 → `ui_*`·스크린샷 도구 사용 가능, 사용자가 화면으로 같이 봄. **포트가 겹치면 다른 세션의 앱을 가로챈다** → 쓰는 포트는 STATE에 적는다
- **FilmCraft CLI에는 read/write root 옵션이 없다** → 파일 경로를 항상 프로젝트 안으로 직접 지정
- `.mcp.json`은 기기별 절대경로라 커밋하지 않는다. 등록·변경 후 **세션 재시작 + 서버 승인** 필요. `/mcp`에서 connected 확인

`.mcp.json` 한 항목 예(윈도우는 경로를 `/` 또는 `\\`로):
```json
{ "mcpServers": { "vectorcraft": { "type": "stdio",
  "command": "C:/Users/<이름>/AppData/Local/ArtCraft/vectorcraft/vectorcraft-cli.exe",
  "args": ["mcp", "--automation-read-root", "C:/…/<repo>", "--automation-write-root", "C:/…/<repo>"] } } }
```

## 공통 함정

1. **export/save 대상 폴더를 자동 생성하지 않는다** → 새 하위 폴더는 먼저 만든다(맥 `mkdir -p`, 윈도우 `New-Item -ItemType Directory -Force`)
2. **DesignCraft 기본 폰트(Source Serif 4)는 한글이 □** → 한글 폰트 지정(`font.replace` 또는 `type.char {attrs:{fontFamily:"Malgun Gothic" | "Apple SD Gothic Neo"}}`). EffectCraft 기본 폰트는 한글 정상. 같은 문서를 두 OS에서 열면 폰트가 서로 없을 수 있으니 PDF/PNG로 내보낸 결과를 공유
3. 앱 본체에 `--help`를 주면 창이 뜬다(DesignCraft는 파일로 해석) → 도움말은 `*-cli`로. `--version` 출력 형식도 앱마다 다르다(SoundCraft는 `SoundCraft CLI x.y.z`)
4. 앱을 업데이트하면 CLI도 같은 버전으로. **이미 열려 있는 세션의 MCP 프로세스는 옛 바이너리로 계속 돈다** → `/mcp`로 재연결하거나 새 세션
5. 명령 id는 짐작하지 말고 `command_list`(filter/menu, `brief:true`)로 찾는다. 짐작이 틀렸던 예: 삭제는 `object.delete`가 아니라 VectorCraft `layer.delete {ids}` / EffectCraft `edit.clear {layers}`, 정렬은 `object.arrange.bringToFront` / EffectCraft `layer.arrange {layers,to|above}`
6. 윈도우 명령줄 길이 한도 32,767자 — 큰 파라미터(긴 path `d`, 배치 JSON)는 도구 호출에 싣지 말고 파일로 두고 `run` 서브커맨드(jsonl) 사용

## 앱별 흐름 (이전 프로젝트에서 검증된 것)

### VectorCraft
- `file.new {name,width,height,units:"Pixels",artboards,artboardLayout:{layout:"row"|"column",spacing}}` — 여러 시안은 아트보드로 나눠 한 문서에
- 그리기: `command_batch`에 `draw_path {d, fill, stroke, strokeWidth, cap, join}` / `draw_shape` 여러 개 → 한 번에. 채움만이면 `stroke:"none"` 명시
- 그라데이션: `fill: {gradient:{kind:"linear", angle:-90, stops:[{offset,color,opacity?}]}}` (angle -90 = 위→아래)
- 복제·이동 `object.move {ids,dx,dy,copy:true}`(새 id 반환) · 크기 `object.scale {ids,sx,sy,origin,strokes:true}` · 숨김 `object.hide {ids}` / `object.showAll`
- 여러 문서: `document.activate {index}`
- 확인 `render_preview {artboard}` → 내보내기 `export {path, artboard|range, scale}`. `range`로 여러 아트보드면 파일명이 `<이름>-Artboard-N.<ext>`로 나뉜다(래스터는 `options:{useArtboards:true}`)
- 조각별 투명 PNG(모션 소스용): 나머지를 `object.hide` 하고 같은 아트보드를 반복 export → 좌표가 그대로 맞는다
- SVG export는 경로가 깔끔해 Compose `addPathNodes(d)`·Android VectorDrawable `pathData`·웹 SVG로 그대로 옮길 수 있다. 앱 아이콘은 108dp=432px 아트보드에 안전 영역(가운데 72dp 보임, 66dp 원) 안쪽으로

### EffectCraft
- `comp.new {name,width,height,frameRate,duration}` → `layer.newSolid {color}` / `file.import {paths, addToComp:true}` / `layer.newShape {kind,size,fill,position}` / `shape.newPath {vertices, closed, space:"comp", fill, stroke:false}`
- 속성 경로는 `get_layer {flat:true}`로 확인: `transform/anchor`, `transform/position`, `transform/scale`(vec3 %), `transform/opacity`, 셰이프 경로 `contents/group/contents/path/path`
- 셰이프 경로 키프레임 값: `{closed, in_tangents, out_tangents, vertices}` (vertices는 **레이어 좌표** = comp 좌표 − 레이어 position). 꼭짓점 수가 같으면 모양 변형(morph)
- `add_keyframe {layer,path,keys:[{time,value}],interpolation:"easyEase"}`, 확인 `render_frame {time}`
- 렌더: `renderQueue.add {comp, format:"h264", output}` → `renderQueue.render {wait:true}`. 같은 출력으로 다시 렌더할 땐 `renderQueue.remove {index}` 먼저. 프로젝트 저장 `save_project {path:".ecproj"}`
- 스케일로 늘리면 위 레이어(작은 부품)도 같이 찌그러진다 → 움직이는 부품은 별도 레이어로

### DesignCraft
- `new_document` → `execute frame.create {rect,content:"text",text}` → 한글 폰트 지정(함정 2) → `render_page`로 확인 → PDF/PNG export. 좌표는 포인트(Letter 612×792, y 아래로)

### PhotoCraft
- `doc_open`/`doc_new` → `command_list`로 id 확인 → `command_run`(한 명령 = 한 히스토리) → `render_preview` → `doc_save`(확장자로 export 형식 결정). 경로는 read/write root 기준 상대경로

### FilmCraft
- 시간 단위는 ticks (1초 = 254016000000). 명령은 `seconds`·`frame`·`timecode`로도 받는다
- 편집 루프: `sequence_inspect`로 id 확인 → `command_run` → `render_frame`(bridge면 `ui_screenshot`)으로 확인 → 틀리면 `edit.undo`
- 원본 확인은 `project_inspect`. 앱을 처음 띄우면 데모 프로젝트가 열려 있으니 새 프로젝트로 시작
- **bridge 모드의 `render_frame`은 창 스크린샷**이라 `seconds`가 안 먹고 창이 가려지면 "no frame was presented" → `playhead.set {seconds}` 후 호출하거나 `file.exportFrame {path, time}`, 구간은 `file.exportMedia {range:"custom", startSeconds, endSeconds, scale:0.5, wait:true}`로 뽑아 ffmpeg 컨택트 시트
- **키프레임 대량 주입은 CLI**: `{"id","params"}` 한 줄씩 jsonl → `filmcraft-cli --bridge 127.0.0.1:<port> --keep-going run kf.jsonl`. `effects.setParam {clip, effect:"motion", param:"position", value:[x,y], time:<시퀀스 ticks>, keyframe:true}`
- **키프레임 전부 지우기는 `effects.toggleAnimation`** — `effects.resetParam`은 값만 되돌린다
- **마스크 키프레임**은 `effects.setParam {clip, effect, param:"path"|"opacity"|"feather", mask:n, value, time, keyframe:true}` (`masks.set`의 `time`은 키프레임을 안 만든다). 타원 path는 꼭짓점 4개 + 핸들 0.5523·반지름
- `masks.track`은 빠르지만 피사체가 화면 밖으로 반쯤 나가는 핸드헬드 컷에선 놓친다 → 얼굴 따라가기는 OpenCV 검출+옵티컬 플로우로 매 프레임 키프레임(이전 프로젝트에 스크립트 있음)
- **폰 영상은 가변 프레임레이트** → 외부 스크립트에서 시간은 프레임번호÷fps가 아니라 PTS(`cv2.CAP_PROP_POS_MSEC`·ffprobe `pts_time`)로. FilmCraft가 타임라인 t에 보여주는 원본 프레임은 pts ≤ (t − 클립 시작)인 마지막 프레임
- **클립 시작 시각은 ticks를 그대로 쓴다.** 초로 환산해 어림하면 1프레임씩 어긋난다
- `file.import {paths}` → 아이템 id, `timeline.place {item, track:"V2", seconds, duration, audio:false}`로 PNG 오버레이 배치. 겹친 클립 끄고 보기는 `clip.enable {clips}`(토글)

### SoundCraft
- `new_session`/`open_session` → `import_audio` → `list_commands`로 id → `execute`/`batch` → `inspect_session`으로 확인 → `bounce_mix`(WAV). 위치는 샘플 정수·`{"seconds":x}`·`"0:12.500"`

## 결과 보여주기
- 렌더 이미지는 사용자 화면에 띄운다(맥 `open`, 윈도우 `ii`). MP4가 "안 보인다"면 파일부터 의심하지 말고 `ffmpeg -ss <t> -frames:v 1`로 프레임을 뽑아 확인 → 대개 플레이어가 같은 파일명의 예전 창을 그대로 둔 것. GIF(`ffmpeg … palettegen/paletteuse`)로 브라우저에서 보는 것도 방법
- 시안은 여러 개(A/B/C) 만들어 비교 시트로 보여주고 선택지 + 추천으로 묻는다
