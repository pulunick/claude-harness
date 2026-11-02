---
name: craft
description: ArtCraft 크래프트 앱(VectorCraft·PhotoCraft·EffectCraft·DesignCraft·FilmCraft·SoundCraft) MCP 공통 사용법·함정·작업 흐름(맥·윈도우). 로고·아이콘·벡터 그래픽, 이미지 편집·합성, 모션·타이틀 렌더, 레이아웃·PDF, 영상 편집, 오디오 믹스를 크래프트 MCP 도구(mcp__vectorcraft__* 등)로 할 때, 또는 새 프로젝트에 크래프트 MCP를 붙이거나 연결이 안 될 때 먼저 읽는다. 프로젝트별 연결·폴더·용도는 각 프로젝트 CLAUDE.md "크래프트" 절이 우선.
---

# 크래프트 앱 공통 가이드 (맥 · 윈도우)

ArtCraft(storytold) 앱 6종. 각 앱의 **CLI `mcp` 서브커맨드가 stdio MCP 서버**다. 하네스 team 프로젝트는 `setup/` 스크립트가 CLI를 설치하고 `.mcp.json`을 만들어 준다.

**층 나누기 (2026-10-19):** 이 스킬 = 모든 프로젝트 공통 지식. **연결 방식·읽기/쓰기 루트·포트·작업 폴더·용도는 각 프로젝트의 `.mcp.json` + CLAUDE.md "크래프트" 절**이 정하고, 이 문서와 충돌하면 프로젝트가 우선. 새로 알게 된 *공통* 함정은 여기에, 프로젝트 고유 사항은 프로젝트에 적는다.

**두 벌 관리:** 정본은 작성자 기기의 전역 `~/.claude/skills/craft/SKILL.md`, 하네스 `optional/craft/skills/craft/SKILL.md`는 **같은 내용의 사본**(2026-11-02 합침). 한쪽을 고치면 그대로 복사해 맞춘다 — 개인 절대경로는 넣지 않는다(`<홈>` 자리표시자).

| 앱 | 급 | 주 용도 | CLI 이름 |
|---|---|---|---|
| VectorCraft | Illustrator | 로고·워드마크·UI 아이콘·앱 아이콘 → SVG/PNG | `vectorcraft-cli` |
| PhotoCraft | Photoshop | 사진 보정·크롭·레이어 합성·누끼 보조 | `photocraft-cli` |
| EffectCraft | After Effects | 로고 모션·타이틀·홍보 모션 → MP4/PNG 시퀀스 | `effectcraft-cli` |
| DesignCraft | InDesign | 일정표·기획서·원페이저 → PDF/PNG | `designcraft-cli` |
| FilmCraft | Premiere | 컷 편집·자막·홍보 영상 → MP4 | `filmcraft-cli` |
| SoundCraft | Pro Tools | 효과음·배경음 다듬기, 영상 오디오 믹스 → WAV | `soundcraft-cli` |

그림 자체(일러스트·캐릭터·사진) 생성은 크래프트가 아니라 이미지 생성 도구 몫 — 전역 스킬 `codex-image`(Codex image_gen + 크로마키 후처리)가 있으면 그것. 크래프트는 벡터·편집·모션·레이아웃.

확인한 버전(2026-11-02): Vector 0.20.0 · Photo 0.19.0 · Effect 0.20.0 · Design 0.16.0 · Film 0.16.0 · Sound 0.16.0 (GUI·CLI 동일).

## 설치 위치 (OS별)

| | 맥 | 윈도우 |
|---|---|---|
| GUI 앱 | `/Applications/<App>.app` (getartcraft.com 런처 또는 dmg) | portable: `%LOCALAPPDATA%\ArtCraft\<app>\<app>.exe` · MSI: `C:\Program Files\<App>\<app>.exe` |
| CLI | `~/.local/bin/<app>-cli` (릴리스의 `<app>-cli-<ver>-macos-universal.zip`) | **GUI와 같은 폴더의 `<app>-cli.exe`** (portable zip·MSI 둘 다 포함, PATH엔 없음) |
| 설치 스크립트 | `setup/mac/install-craft.sh` (`--force` = 전부 최신) | `setup/windows/install-craft.ps1` |
| 파일 열어 보여주기 | `open <파일>` | `Start-Process <파일>` (= `ii`) |
| 한글 폰트 | `Apple SD Gothic Neo` | `Malgun Gothic` |

윈도우 릴리스에는 CLI 단독 zip이 없다 — 앱 zip/MSI 안에 `<app>-cli.exe`가 같이 들어 있다(2026-10-25 확인). 업데이트는 앱 폴더를 새 zip으로 통째 교체.

## 연결 방식

- **headless** (기본 추천): `<cli> mcp --automation-read-root <폴더> --automation-write-root <폴더>` — 창 없이 엔진만, 파일 접근을 그 폴더로 제한. 루트는 여러 번 줄 수 있고, 빠진 쪽은 접근 0. **FilmCraft는 0.16에도 루트 옵션이 없다**(`filmcraft-cli mcp`만, 제한 없음)
- **bridge(앱 연결)**: 앱을 `--control <port>`로 띄우고(맥 `open -a <App> --args --control <port>`, 윈도우 `& "<app>.exe" --control <port>`) MCP를 그 포트에 붙임 → `ui_*`·스크린샷 도구 사용 가능, 사용자가 화면으로 같이 봄. **앱마다 플래그 이름이 다르다**(2026-11-02 `mcp --help` 기준):

  | 앱 | bridge 플래그 | 비고 |
  |---|---|---|
  | VectorCraft | `--connect 127.0.0.1:<port>` (`--bridge`는 오류) | **인자 없는 `mcp`는 7979의 앱에 붙고, 앱이 없으면 headless로 자동 전환** — 루트 플래그를 주면 headless 고정. **이 선택은 MCP 서버가 뜰 때 한 번만** 한다 → 세션을 연 뒤 앱을 켜면 headless 그대로라 `ui_screenshot`이 "needs the desktop app" → 앱을 먼저 켜고 세션을 열거나 `/mcp` 재연결(붙으면 `Backend: remote 127.0.0.1:7979`, for-her 2026-11-02) |
  | PhotoCraft | `--bridge <port>` + `--control-token`/`--control-token-file` | bridge에선 루트 플래그 거부(루트는 앱 설정에서). 앱 설정 Integrations의 Allow Agent Control·Control Port(0.17+) |
  | EffectCraft | `--bridge <port>` | |
  | DesignCraft | `--connect <port>` | |
  | FilmCraft | `--bridge 127.0.0.1:<port>` | 제어 토큰 필수(아래) |
  | SoundCraft | `--connect <port>` | 루트·`--demo`와 같이 못 씀 |

  - **FilmCraft 0.13+는 제어 토큰 필수**: 앱을 `open --env FILMCRAFT_CONTROL_TOKEN=<64자리 hex> -a FilmCraft --args --control <port>`로 띄우고, MCP도 같은 값을 env로(`.mcp.json`에서 `/bin/zsh -c 'FILMCRAFT_CONTROL_TOKEN=$(<토큰파일) exec filmcraft-cli mcp --bridge …'`). 토큰 없이 띄우면 포트가 안 열려 `Connection refused`, 값이 다르거나 없으면 `control authentication failed; closing the connection`(0.16도 같음). 토큰은 저장소 밖 파일(`~/.config/artcraft/filmcraft-control-token`)에. 하네스 film 모듈의 `tools/craft.sh film|effect|vector`가 포트를 `.mcp.json`에서 읽어 토큰까지 맞춰 띄운다
  - **포트가 겹치면 다른 세션의 앱을 가로챈다.** 작성자 기기 점유: FilmCraft 9876 · EffectCraft 9877 · VectorCraft 7979 = for-her 전용. 다른 프로젝트는 headless를 쓰거나 다른 포트를 골라 STATE·이 목록에 적는다. VectorCraft를 인자 없이 붙이면 for-her 앱(7979)에 붙을 수 있으니 다른 프로젝트는 루트 플래그를 꼭 준다
- `.mcp.json`은 기기별 절대경로라 커밋하지 않는다. 등록·변경 후 **세션 재시작 + 서버 승인** 필요. `/mcp`에서 connected 확인

`.mcp.json` 한 항목 예(윈도우는 경로를 `/` 또는 `\\`로, CLI는 앱 폴더의 `<app>-cli.exe`):
```json
{ "mcpServers": { "vectorcraft": { "type": "stdio",
  "command": "<홈>/.local/bin/vectorcraft-cli",
  "args": ["mcp", "--automation-read-root", "<프로젝트 절대경로>", "--automation-write-root", "<프로젝트 절대경로>"] } } }
```
작업 폴더 관례: 원본 `craft/{vector,photo,effect,design,film,sound}/`, 결과물 `craft/out/`.

## 공통 함정

1. **export/save 대상 폴더를 자동 생성하지 않는다** → 새 하위 폴더는 먼저 만든다(맥 `mkdir -p`, 윈도우 `New-Item -ItemType Directory -Force`)
2. **DesignCraft 기본 폰트(Source Serif 4)는 한글이 □**(0.16에서도 그대로, 2026-11-02 재확인) → **문서를 만들자마자 기본 문단 스타일을 바꾼다**: `execute style.paragraph.edit {name:"[Basic Paragraph]", chars:{fontFamily:"Apple SD Gothic Neo" | "Malgun Gothic", size:…}}` → 이후 만드는 텍스트 프레임이 전부 한글 정상. 스타일 이름은 대괄호 포함(`"Basic Paragraph"`는 "no style"). `font.replace {family:"Source Serif 4", toFamily:…}`는 **이미 있는 텍스트만** 바꾸고 뒤에 만든 프레임은 다시 □. `type.char {attrs:{…}}`는 선택된 텍스트에만 적용되고 크기도 `attrs` 안(`{size:24}`처럼 바깥에 두면 무시). EffectCraft 기본 폰트는 한글 정상. 같은 문서를 두 OS에서 열면 폰트가 서로 없을 수 있으니 PDF/PNG로 내보낸 결과를 공유
3. 앱 본체에 `--help`를 주면 창이 뜬다(DesignCraft는 파일로 해석) → 도움말은 `*-cli`로(DesignCraft는 `designcraft-cli mcp --help`도 오류 → 오류 메시지의 usage를 본다). `--version` 형식이 앱마다 다르다(`photocraft-cli 0.19.0 (해시, 날짜)`, `soundcraft-cli 0.16.0 (macos aarch64)` — 0.13까진 `SoundCraft CLI x.y.z`) → 버전은 숫자 패턴으로 뽑는다
4. 앱을 업데이트하면 CLI도 같은 버전으로(맥 `install-craft.sh --force`). CLI는 `~/.local/bin` 하나를 모든 프로젝트가 같이 쓰므로 한 번 교체하면 전부 적용되지만, **이미 열려 있는 세션의 MCP 프로세스는 옛 바이너리로 계속 돈다** → 그 세션에서 `/mcp`로 재연결하거나 새 세션. 릴리스 조회는 GitHub API라 **비인증 시간당 60회 한도에 걸리면 403** → 스크립트는 `gh api`(로그인 시)나 `GITHUB_TOKEN`을 쓴다
5. 명령 id는 짐작하지 말고 목록 도구로 찾는다 — `command_list`(Vector·Photo·Film·Effect) / `list_commands`(Vector·Effect·Design·Sound, EffectCraft는 `compact:true`). CLI로는 `<cli> commands`(Film은 `commands <필터> --json`, `describe <id>`). 짐작이 틀렸던 예: 삭제는 `object.delete`가 아니라 VectorCraft `layer.delete {ids}` / EffectCraft `edit.clear {layers}`, 정렬은 `object.arrange.bringToFront` / EffectCraft `layer.arrange {layers,to|above}`. **단위도 params 설명에서 확인**(VectorCraft `object.scale`의 `sx`는 %)
6. 윈도우 명령줄 길이 한도 32,767자 — 큰 파라미터(긴 path `d`, 배치 JSON)는 도구 호출에 싣지 말고 파일로 두고 `run --commands <파일.jsonl>`(Vector·Effect) / `run <파일.jsonl>`(Film)
7. **경로 제한(루트) 아래에선 더 막힌다** — EffectCraft 0.19+: `run_script`/`script.run` 거부, 렌더 출력이 쓰기 루트 밖이면 거부, `output` 없는 `renderQueue.add`는 저장된 프로젝트 필요, 루트 밖 푸티지는 안 보임. PhotoCraft는 쓰기 루트의 이미지가 아닌 파일을 덮어쓰지 않는다. 출력 경로는 루트 안 상대·절대경로로

## 앱별 흐름 (검증된 것)

### VectorCraft
- `file.new {name,width,height,units:"Pixels",artboards,artboardLayout:{layout:"row"|"column",spacing}}` — 여러 시안은 아트보드로 나눠 한 문서에
- 그리기: `draw_path {d, fill, stroke, strokeWidth, cap, join}` / `draw_shape`. 채움만이면 `stroke:"none"` 명시. MCP `command_batch`는 엔진 명령(`{id,params}`)만 받고 `draw_path` 같은 MCP 도구는 못 넣는다 → 많이 그릴 땐 `draw_path`를 여러 번(id가 호출 순서대로 붙어 z-order도 그 순서)
- 그라데이션: `fill: {gradient:{kind:"linear", angle:-90, stops:[{offset,color,opacity?}]}}` (angle -90 = 위→아래)
- 복제·이동 `object.move {ids,dx,dy,copy:true}`(새 id 반환) · 크기 `object.scale {ids, sx, sy, origin:[x,y], strokes:true}` · 숨김 `object.hide {ids}` / `object.showAll`
  - **`object.scale`의 `sx`·`sy`는 퍼센트** — `sx:0.5`는 0.5%라 점(1×1)으로 뭉개진다. 절반은 `sx:50`. `origin:[x,y]`(문서 좌표)은 정상 동작(2026-11-02 재현 확인. 10-27 zooroom 로고가 점이 된 원인)
  - `export {artboard}`의 artboard 인덱스는 **0-based**. 아트보드별 SVG는 좌표가 그 아트보드 원점 기준으로 재배치돼 나온다 → 라이트/다크 아트보드의 SVG 경로가 같아 색만 치환하면 된다
- 여러 문서: `document.activate {index}`. 상태 확인 `doc_inspect`/`document.inspect`(오브젝트 bounds·id)
- 확인 `render_preview {artboard}` → 내보내기 `export {path, artboard|range, scale}`. `range`로 여러 아트보드면 파일명이 `<이름>-Artboard-N.<ext>`로 나뉜다(래스터는 `options:{useArtboards:true}`)
- **픽셀 크기로 내보내기**(0.19+, 2026-11-02 headless 검증): `document.export {path, artboard, width:512}` → 512×512 (스키마 설명엔 없지만 동작)
- **크기별 일괄 내보내기 `document.exportForScreens`**(검증):
  - Android 런처 아이콘(108dp = 432px 아트보드): `{folder, artboards:[0], folders:"rows", name:"ic_launcher_foreground", formats:[{format:"png", width:108, folder:"mipmap-mdpi", suffix:""}, …162 hdpi, 216 xhdpi, 324 xxhdpi, 432 xxxhdpi]}` → `mipmap-*/ic_launcher_foreground.png`
  - **`preset:"density"`는 아트보드 크기를 mdpi(1x)로 본다** → 432px 아트보드면 xxxhdpi가 1728px로 4배 크게 나온다. 런처 아이콘은 위처럼 width를 직접 주거나 아트보드를 dp 크기(108px)로
  - iOS·웹 배율: `preset:"mobile"` → `1x/`·`2x/`·`3x/` 폴더에 `@2x`·`@3x` 접미사. 아트보드마다 한 벌씩(이름은 아트보드 이름 → `artboard.setProps {artboards:[{index, name}]}`로 먼저 붙인다)
  - 행별 `folder`는 **`folders:"rows"`를 같이 줘야 적용**된다(없으면 한 폴더에 `-2`, `-3`으로 쌓인다)
  - `width` 행의 기본 접미사는 `@1024w`, 배율 행은 `@2x` → 이름 패턴에 `<scale>`을 쓰면 `-2x@2x`처럼 겹치니 `suffix:""`
  - 스토어 512px·1024px·SVG를 한 번에: `formats:[{format:"png", width:1024}, {format:"png", width:512, suffix:"_play"}, {format:"svg"}]`. `zip:true`면 한 zip으로
- 조각별 투명 PNG(모션 소스용): 나머지를 `object.hide` 하고 같은 아트보드를 반복 export → 좌표가 그대로 맞는다
- SVG export는 경로가 깔끔해(`d` 몇 줄) Compose `addPathNodes(d)`·Android VectorDrawable `pathData`·웹 SVG로 그대로 옮길 수 있다. 앱 아이콘은 108dp=432px 아트보드에 안전 영역(가운데 72dp 보임, 66dp 원) 안쪽으로
- 앱 없이 한 번에: `vectorcraft-cli run --commands steps.jsonl --export out.svg` (`{"command","params"}` 한 줄씩, 앞 단계 결과는 `"$N.id"`로 참조, N은 0부터)

### EffectCraft
- `comp.new {name,width,height,frameRate,duration}` → `layer.newSolid {color}` / `file.import {paths, addToComp:true}` / `layer.newShape {kind,size,fill,position}` / `shape.newPath {vertices, closed, space:"comp", fill, stroke:false}`
- 속성 경로는 `get_layer {flat:true}`로 확인: `transform/anchor`, `transform/position`, `transform/scale`(vec3 %), `transform/opacity`, 셰이프 경로 `contents/group/contents/path/path`. 열거형 속성은 `get_property`/`get_layer`가 선택지를 같이 알려 준다(0.19+)
- 셰이프 경로 키프레임 값: `{closed, in_tangents, out_tangents, vertices}` (vertices는 **레이어 좌표** = comp 좌표 − 레이어 position). 꼭짓점 수가 같으면 모양 변형(morph)
- `add_keyframe {layer,path,keys:[{time,value}],interpolation:"easyEase"}`, 확인 `render_frame {time}`
- 렌더: `renderQueue.add {comp, format:"h264", output}` → `renderQueue.render {wait:true}`. 같은 출력으로 다시 렌더할 땐 `renderQueue.remove {index}` 먼저. 프로젝트 저장 `save_project {path:".ecproj"}`. 루트 제한 시 함정 7
- comp 전체 크기 바꾸기는 `comp.scale {comp, factor | width | height}`(레이어 위치·키·카메라까지 한 배율, 0.19+). **비율은 유지** — 정사각 → 세로 같은 비율 변경은 안 된다(2026-11-02 검증)
- **내장 애니메이션 프리셋 68종**(`anim.builtinPresets` 목록 → `anim.applyBuiltinPreset {preset, layers:[id]}`, 2026-11-02 headless 검증): Transitions 23(`fadeIn`·`lensPopIn`·`wipeInFromLeft`·`cardFlipIn`…) · Behaviors 22(`pulse`·`breathe`·`floatUpDown`·`spinSlow`·`wiggleSoft`·`heartbeat`…) · Backgrounds 23(`softGradientDrift`·`auroraVeil`·`bokehDrift`…). 스플래시·온보딩 모션 시안에 적합
  - **Behaviors는 transform에 익스프레션**을 넣는다(`pulse` = scale에 sin, `spinSlow` = `value + time*36`). 결과의 `effects`가 `[]`여도 적용된 것 → `get <comp> <layer> transform/scale --json`의 `expression`으로 확인. **같은 속성의 Behavior를 또 붙이면 앞의 것을 덮어쓴다**(pulse → breathe면 breathe만)
  - Transitions는 키프레임(`fadeIn` = opacity 0→100, 0.5초)이나 이펙트(`lensPopIn`)로 들어가 Behavior와 겹쳐 쓸 수 있다
  - 텍스트는 별도 `layer.applyTextPreset {layer, preset: typewriter|fadeUpCharacters|bounceInWords|trackingIn|scramble|blurIn|jitter|dropInLines}`
  - CLI 한 번에: `effectcraft-cli --project a.ecproj run anim.applyBuiltinPreset '{"preset":"pulse","layers":[2]}' … --save-as b.ecproj` → `render --comp <이름> --out x.mp4 --format h264`(1080² 3초 ≈ 0.5초). 레이어 id는 `info`로(`layer.arrange`에 음수 인덱스는 안 된다)
- 스케일로 늘리면 위 레이어(작은 부품)도 같이 찌그러진다 → 움직이는 부품은 별도 레이어로

### DesignCraft
- `new_document` → 기본 문단 스타일에 한글 폰트(함정 2) → `execute frame.create {rect,content:"text",text}` → `render_page`로 확인 → PDF/PNG export. 좌표는 포인트(Letter 612×792, y 아래로)

### PhotoCraft
- `doc_open`/`doc_new` → `command_list`로 id 확인 → `command_run`(한 명령 = 한 히스토리) → `render_preview` → `doc_save`(확장자로 export 형식 결정). 경로는 read/write root 기준 상대경로(절대경로도 루트 안이면 됨, 0.18+)
- **배경 제거 `layer.removeBackground {refine:true}`**(2026-11-02 검증): 별도 모델 다운로드 없이 헤드리스에서 0.2초(2816×1536). 크림색 배경의 일러스트 시트에서 캐릭터 6개를 한 번에 깔끔히 → `photocraft-cli run in.png --cmd layer.removeBackground --params '{}' --out out.png`(마스크는 PNG 저장 때 합쳐짐)
  - **배경색과 비슷한 부분(크림 배경 위 흰 모자·거품기)은 같이 지워진다** → 결과를 마젠타 등 대비색 위에 합성해 확인. 흰 요소가 중요하면 Codex 크로마키(초록 배경 생성) 쪽이 낫다
  - `select.object {point}`(클릭한 물체)는 **선화 일러스트엔 못 쓴다** — 얼굴 채색이나 몸통처럼 한 영역만 잡고 외곽선은 구멍. 사진용으로 보이며 사진으론 미검증
  - 시트에서 캐릭터를 하나씩 떼어 내는 건 사각 선택으론 이웃이 섞인다 → 처음부터 한 장에 하나씩 생성하는 편이 낫다
  - 레이어 지정은 id로: PNG를 열면 원본은 "Background"가 아니라 `Layer 0`(id 2). `layer.delete {layer:id}`(키가 `layers`면 무시되고 선택 레이어가 지워진다)
- **레이어별 PNG(UI 에셋 추출)**(2026-11-02 검증): MCP `doc_export_layers {dir, prefix}`는 레이어마다 **문서 전체 크기** PNG. **투명 여백을 잘라 내용 크기로 뽑으려면 엔진 명령 `file.export.layersToFiles {dir, trim:true}`인데, MCP 헤드리스(루트 제한)에선 "ambient filesystem paths"라 막힌다** → CLI로: `photocraft-cli run ui.psd --cmd file.export.layersToFiles --params '{"dir":"out","trim":true}'` (60×60 배지, 200×200 아바타, 800×160 버튼처럼 정확히, 바깥은 완전 투명)
  - 파일명은 `<prefix>_0000_<레이어명>.png`로 번호가 붙고(`prefix:""`면 `layer_`), 번호는 못 뺀다 → 내보낸 뒤 이름 정리
  - 비어 있는 레이어(새 문서의 기본 "Layer 1")도 문서 전체 크기로 같이 나온다 → 지우고 내보내거나 결과에서 버린다
  - 새 문서: `photocraft-cli run --new '{"width":1080,"height":1920,"background":"transparent"}' --cmd layer.new.layer --params '{"name":"btn"}' --cmd select.rect --params '{"x":…,"y":…,"width":…,"height":…,"ellipse":false}' --cmd edit.fill --params '{"contents":"color","color":"#3B6BF5"}' … --out ui.psd`

### FilmCraft
- 시간 단위는 ticks (1초 = 254016000000). 명령은 `seconds`·`frame`·`timecode`로도 받는다
- 편집 루프: `sequence_inspect`로 id 확인 → `command_run` → `render_frame`(bridge면 `ui_screenshot`)으로 확인 → 틀리면 `edit.undo`
- 원본 확인은 `project_inspect`(빈·아이템 id·길이). 앱을 처음 띄우면 데모 프로젝트("FilmCraft Demo")가 열려 있으니 새 프로젝트로 시작
- **bridge 모드의 `render_frame`은 창 스크린샷**이라 `seconds` 인자가 안 먹고 창이 가려지면 "no frame was presented" → `playhead.set {seconds}` 후 호출하거나, 시간 지정은 `file.exportFrame {path, time}`, 구간 확인은 `file.exportMedia {range:"custom", startSeconds, endSeconds, scale:0.5, wait:true}`(43초 반해상도 ≈ 8초)로 뽑아 ffmpeg 컨택트 시트
- **키프레임 대량 주입은 CLI**: `{"id","params"}` 한 줄씩 jsonl → `filmcraft-cli --bridge 127.0.0.1:<port> --keep-going run kf.jsonl` (MCP `command_batch`는 `steps`, 큰 JSON을 도구 호출에 싣기 부담). `--keep-going`은 실패한 줄을 건너뛰고 끝까지 돌지만 **한 줄이라도 실패하면 종료 코드 1** → 스크립트에서 성공 판정은 출력의 실패 줄로. `effects.setParam {clip, effect:"motion", param:"position", value:[x,y], time:<시퀀스 ticks>, keyframe:true}`
- **키프레임 전부 지우기는 `effects.toggleAnimation`** — `effects.resetParam`은 키프레임을 안 지우고 값만 되돌린다
- **마스크 키프레임**은 `effects.setParam {clip, effect, param:"path"|"opacity"|"feather", mask:n, value, time, keyframe:true}` (`masks.set`의 `time`은 키프레임을 안 만들고 정적값만 바꾼다). 타원 path는 꼭짓점 4개 + 핸들 0.5523·반지름. 지우기도 `effects.toggleAnimation {…, mask:n}`
- `masks.track`은 빠르지만(90프레임 1.9초) 피사체가 화면 밖으로 반쯤 나가는 핸드헬드 컷에선 몇 초 만에 놓친다 → 얼굴 따라가기는 OpenCV YuNet 검출+옵티컬 플로우로 매 프레임 키프레임이 안정적(for-her `tools/face_track.py`, `face_overlay_keyframes.py`, 검수 `contact_sheet.py`)
- **폰 영상은 가변 프레임레이트** → 외부 스크립트에서 시간은 프레임번호÷fps가 아니라 PTS(`cv2.CAP_PROP_POS_MSEC`·ffprobe `pts_time`)로. FilmCraft가 타임라인 t에 보여주는 원본 프레임은 **pts ≤ (t − 클립 시작)인 마지막 프레임**(오프셋 없음)
- **클립 시작 시각은 ticks를 그대로 쓴다.** 초로 환산해 어림하면 틀린다(예: 551655014400000 ticks = 2171.7333s인데 2171.7로 잡으면 1프레임 어긋남). 외부 추적 키프레임은 `클립시작ticks + t×254016000000`, 확인용 `file.exportMedia`의 `startSeconds`도 ticks÷254016000000 그대로
- `file.import {paths}` → 아이템 id, `timeline.place {item, track:"V2", seconds, duration, audio:false}`로 PNG 오버레이 배치. 겹친 클립 끄고 보기는 `clip.enable {clips}`(토글)
- 셸에서: `filmcraft-cli export <out.mp4> --preset … | --format …`, `render --seconds S --out f.png`, `probe <media>`. 오프라인 미디어가 있으면 export가 exit 1(`--allow-offline`로 허용)

### SoundCraft
- `new_session`/`open_session` → `import_audio` → `list_commands`로 id → `execute`/`batch` → `inspect_session`으로 확인 → `bounce_mix`(WAV). 위치는 샘플 정수·`{"seconds":x}`·`"0:12.500"`
- 재생 장치·버퍼(`setup.playback_engine`/`setup.hardware`)는 앱에서만 적용, headless에선 안 된다(0.15+)

## 결과 보여주기
- 렌더 이미지는 사용자 화면에 띄운다(맥 `open`, 윈도우 `ii`). MP4가 "안 보인다"면 파일부터 의심하지 말고 `ffmpeg -ss <t> -frames:v 1`로 프레임을 뽑아 확인 → 대개 같은 파일명이라 플레이어가 예전 창을 그대로 둔 것. 맥은 `osascript -e 'tell application "QuickTime Player" to close every document'` 후 다시 열거나 GIF(`ffmpeg … palettegen/paletteuse`)로 브라우저에서
- 시안은 여러 개(A/B/C) 만들어 비교 시트로 보여주고 선택지 + 추천으로 묻는다
