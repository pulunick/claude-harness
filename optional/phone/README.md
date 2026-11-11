# 실기기 QA — phone-harness로 테스트 폰 확인하기

> 하네스 `optional/phone` 모듈의 공용 문서다(프로젝트엔 `docs/phone-qa.md`로 들어가고 `sync.py`가 덮어쓴다 — 고칠 일은 하네스에서). 규칙 요약은 프로젝트 CLAUDE.md '실기기 QA' 절, 프로젝트 고유 값(기기·앱·메인 화면 id·누르지 않는 문구)은 `tools/phone/phone.json`·`deny.txt`.
> **👤 = 사용자가 직접 실행하는 단계**(세션의 설치·권한 변경은 자동 권한 검사가 막는다). 폰에 앱을 설치·삭제하는 단계는 실행하는 세션이 그 창에서 사용자 허락을 받는다.
> 처음 만든 곳: usroom(2026-11-10, Galaxy Z Flip 4·Android 16). 1·2회차 실사용에서 명령 23번에 사람 개입 4번(예전 방식 추정 20~23번)이라 2026-11-11 모듈로 옮겼다.

## 0. 켜기 (하네스 쪽)

```
python3 <하네스>/setup/sync.py init <프로젝트> --with phone      # 기존 프로젝트에도 — 이 모듈만 더해진다
```
- 공용(덮어씀): `tools/phone/{phonelib.py,preflight,see,tap,shot,type_ko,test_phone.py}`, `docs/phone-qa.md`(이 문서)
- 프로젝트 소유(한 번 생성): `tools/phone/phone.json`, `tools/phone/deny.txt`, CLAUDE.md '실기기 QA' 절. 앱에 묶인 명령이 필요하면 하네스의 `optional/phone/app.py.example`을 `tools/phone/app.py`로 복사해 고친다.

## 1. 설치

### phone-harness (맥)
```
👤 ! uv tool install --python 3.12 phone-harness==0.3.3
👤 ! phone-harness config set platform android
   phone-harness doctor android        # adb·기기·접근성 트리 PASS 확인 (scrcpy FAIL은 선택 항목)
```
- 버전은 `==0.3.3`으로 고정한다. 올릴 땐 하네스의 이 문서와 CLAUDE 절을 같이 고친다. 확인: `phone-harness -V`.
- 출처: https://github.com/phone-harness/phone-harness (MIT). Android는 adb, 화면 읽기는 접근성 트리(OCR 아님 — Compose 문구·content-description까지 정확).

### `tools/phone/phone.json` (프로젝트 소유)
| 키 | 뜻 |
|---|---|
| `serial` | `adb devices`의 기기 번호. 비우면 adb 기본(USB 한 대면 자동). 환경변수 `PHONE_SERIAL`이 우선 |
| `app` | 확인할 앱 패키지(예: `com.example.app`) — 필수 |
| `app_name` | 출력에 쓸 이름 |
| `display_id` | 화면 둘인 폰(Flip 등)의 메인 화면 id. 비우면 `dumpsys SurfaceFlinger --display-id`의 `HWC display 0`에서 자동 |
| `launchers` | 기본(삼성·픽셀·AOSP) 밖의 런처 패키지 — 전면 앱 판정용 |
| `keyboard` | 원래 키보드 IME(손으로 복귀할 때 참고, 헬퍼는 입력 직전 값을 기억해 되돌린다) |

### ADBKeyboard (테스트 폰) — 한글 입력용
- 출처: https://github.com/senzhk/ADBKeyBoard (GPL-2.0)
- 버전: **v2.5-dev** (2026-04-23, "fix keyboard unusable on android-36")
  - 파일 `keyboardservice-debug.apk` 18,753바이트, sha256 `41a8a0996d7397a2390d1ca16a75cb66c4a7bdaa89cf4e63600a4d3fb346fbbb`
  - 주소: https://github.com/senzhk/ADBKeyBoard/releases/download/v2.5-dev/keyboardservice-debug.apk
- 받기와 설치 (**👤 허락 뒤** 세션이 실행, `<serial>`은 phone.json 값):
```
mkdir -p "$SCRATCH/adbkbd" && cd "$SCRATCH/adbkbd"        # 저장소 밖(스크래치패드)
curl -fsSLo adbkeyboard.apk <위 주소>
shasum -a 256 adbkeyboard.apk                               # 위 sha256과 같아야 설치
adb -s <serial> install adbkeyboard.apk
adb -s <serial> shell ime enable com.android.adbkeyboard/.AdbIME
```
- 활성화만 하고 기본 키보드로 두지 않는다. 전환·복귀는 `tools/phone/type_ko`가 입력할 때마다 한다.
- 앱 안 versionName은 `2.0`으로 나온다(릴리스 태그와 다름 — 정상). 설치 직후 첫 `ime enable`은 "Unknown input method"로 실패할 수 있다 — 몇 초 뒤 다시.

### 헬퍼 (`tools/phone/`)
| 명령 | 하는 일 | 종료 코드 |
|---|---|---|
| `preflight [--wait-version V [--timeout 초]]` | adb 상태·전면 앱·화면 켜짐/잠금·네트워크·앱 버전·키보드 출력. `--wait-version`은 그 버전이 깔릴 때까지 기다리고, 전면이 스토어(업데이트하던 화면)면 홈으로 돌린다 | 0 통과 / 1 조건 미달 / 2 adb 미연결·설정 없음 |
| `see "문구" …` · `see --absent "문구"` | 지금 화면 트리에 문구가 있는지(부분 일치, 텍스트·설명). 읽기만 | 0 / 1 |
| `see --dump` | 화면의 글자 있는 노드 전부(위→아래, 누를 수 있는 것 `•`) — 모르는 화면에서 다음 탭 문구 찾기 | 0 |
| `tap "문구"` | 문구가 든 버튼을 누름. 요청 문구와 잡힌 노드의 텍스트·설명을 둘 다 누르지 않는 목록과 대조 | 0 / 1 없음 / 3 거부 |
| `shot <파일>` | 메인 화면 스크린샷. 저장소 안 경로는 거부 | 0 / 2 |
| `type_ko "문장"` | 입력란에 ADBKeyboard로 입력 → 대조 → 키보드 복귀 | 0 / 1 |
| (app.py) 예: `turn "문장"` | preflight → 앱 열기 → 입력 → 보내기 → 응답이 멈출 때까지 대기·출력 | 0 / 1 |

- 테스트(폰 없이): `python3 -m unittest tools/phone/test_phone.py` (공용). 프로젝트 고유 명령·문구는 `test_app.py`에 따로.
- 누르지 않는 목록은 **확정 버튼** 문구다(예: '결제하기'). 항목을 고르기만 하는 칸은 누를 수 있다. 결제 화면이 바뀌면 `deny.txt`도 같이 고친다. `deny.txt`가 없으면 헬퍼는 아무것도 누르지 않는다.

## 2. 되돌리기
- 키보드 복귀(헬퍼가 자동으로 하지만 손으로 할 때): `adb -s <serial> shell ime set <phone.json keyboard>` → `adb -s <serial> shell settings get secure default_input_method`로 확인. 삼성 기본은 `com.samsung.android.honeyboard/.service.HoneyBoardService`.
- 더 안 쓸 때(👤 허락 뒤): `adb -s <serial> shell ime disable com.android.adbkeyboard/.AdbIME` → `adb -s <serial> uninstall com.android.adbkeyboard`
- phone-harness 제거: `👤 ! uv tool uninstall phone-harness` (설정은 `~/.phone-harness/`).

## 3. 알려진 함정
- **화면 둘인 폰(Flip)**: phone-harness `screenshot()`은 adb의 'Multiple displays' 경고가 PNG 앞에 붙어 깨지고, `tap_image_point()`·`image_point()`는 TypeError → 쓰지 않는다. 스크린샷은 `tools/phone/shot`(= `adb exec-out screencap -d <메인 화면 id> -p`).
- **한글**: phone-harness `type_text()`는 한글에서 `adb input text` NullPointerException. 영문 키 이벤트는 한/영을 바꿔도 IME 조합을 안 거친다 → ADBKeyboard(`type_ko`).
- **adb `unauthorized`**: 세션(창)이 바뀌면 나올 수 있다 → 👤 폰 화면의 'USB 디버깅 허용'.
- **잠금**: PIN 잠금은 세션이 풀지 않는다 → 👤. 확인이 길면 폰의 화면 꺼짐 시간을 늘려 두면 개입이 준다.
- **디버그 ↔ 스토어 설치본**: 서명이 달라 덮어 설치가 안 된다. 바꿀 땐 지우고 설치(기기 기록이 지워짐 — 👤 허락).
- **폰 네트워크**: Wi-Fi가 안 붙어 있으면 서버 응답이 필요한 흐름이 실패한다. `preflight`가 먼저 막는다.
- **응답 완료 신호**: 입력 중 표시는 트리에 안 잡히는 경우가 많고, 보내기 버튼 enabled도 신호가 안 될 수 있다. `TurnJudge`는 늘어난 텍스트가 3회 연속(1.5초 간격) 그대로일 때 완료로 본다.
- **고정 대기**: 앱을 연 뒤 `sleep`으로 기다리면 한 턴이 50초를 넘는다(usroom 실측 47~56초 중 판정 11~15초). `wait_stable`이나 기대 문구가 보일 때까지로 기다린다.

## 4. review 문서에 '확인 방법' 적는 법
- **문구 확인**: 화면까지 가는 길 + 명령. 예) `설정 → 결제 안내`에서 `tools/phone/see "결제하고 7일 안에…"` → 0. 없어야 하는 문구는 `see --absent`.
- **흐름 확인**: 예) `tools/phone/turn "안녕"` → 기대: 응답 1개 이상, 실패 문구 없음, 0으로 끝남.
- **이전 글이 사라지는 화면**(대화 화면처럼 새 글이 오면 위 글이 화면 밖으로 밀리는 곳)에선 "보낸 문장이 보이는가"를 확인 방법으로 쓰지 않는다 — 응답 문구나 늘어난 텍스트로 확인한다.
- **결과 적기**: 기기·빌드(`preflight` 출력의 versionName/versionCode)·시각·명령·종료 코드. 텍스트로 확인 못 한 것(그림·색·배치)은 "미확인" 또는 `shot` 경로(저장소 밖)와 함께 눈으로 본 결과로 남긴다.
- 결제·해지·탈퇴·로그아웃은 헬퍼가 누르지 않는다. 그 흐름은 "사용자 직접 확인"으로 적는다.
- **실기기 미확인**: 단위 테스트로만 확인한 것(예: 같은 줄 다른 문구로 요청했을 때의 노드 단계 거부)은 실기기에서 한 번 확인할 때까지 "unittest만"으로 적는다.

## 5. 효율 기록 (선택 — 도입 초기나 헬퍼를 바꾼 뒤)
실기기 확인 결과를 적을 때 항목마다 세 칸을 더한다. 예전 방식(사람이 폰을 만지고 결과를 말로 전달)과 비교할 숫자를 남기려는 것이다.
- **개입**: 사람 개입 횟수와 종류 — `!` 실행 / 폰 직접 조작(adb 허용·잠금 해제·결제) / 결과를 말로 전달. 없으면 `0`.
- **끝남**: `명령`(종료 코드) / `육안`(shot을 눈으로 봄) / `사용자`(사용자 직접 확인).
- **시간·비교**(가능하면): 걸린 시간, 예전 방식이면 사람 손이 몇 번 갔을지 한 줄.

한 묶음이 끝나면 합계(명령 n / 육안 n / 사용자 n, 개입 총횟수). 헬퍼 결함·규칙 후보는 하네스 템플릿 세션(`claude-harness-*`)에 보낸다.

| 항목 | 명령 | 종료 | 개입 | 끝남 | 시간·비교 |
|---|---|---|---|---|---|
| 환불 문구 | `see "결제하고 7일 안에…"` | 0 | 0 | 명령 | 20초 · 예전: 화면 이동+읽어 전달 2회 |
