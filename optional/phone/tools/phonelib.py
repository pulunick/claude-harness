"""실기기 QA 헬퍼 — 하네스 optional/phone 모듈(공용 파일, sync.py가 덮어쓴다. 고칠 일은 하네스에서). 절차는 docs/phone-qa.md.

명령: preflight · see · tap · shot · type_ko  (tools/phone/<명령> 래퍼가 부른다) + 프로젝트의 app.py가 더하는 명령
- 화면 읽기·탭은 phone-harness(접근성 트리)로, 스크린샷·키보드 전환·상태 확인은 adb로 직접.
- phone-harness가 필요한 명령은 `phone-harness`에 이 파일을 불러오는 짧은 스크립트를 넘겨,
  그 안의 헬퍼(ui·tap·open_app·wait_stable)를 `h`로 받아 쓴다. 폰 없는 테스트는 가짜 `h`를 넣는다.
- 탭은 `safe_tap` 하나로만 한다. 누르지 않는 목록(deny.txt)의 문구는 거부한다. 좌표 탭은 밖으로 내보내지 않는다.
- 프로젝트 고유 값은 tools/phone/phone.json(프로젝트 소유), 앱에 묶인 명령(예: 대화 한 턴 `turn`)은 tools/phone/app.py(프로젝트 소유).
  app.py 는 `HARNESS_CMDS`·`ADB_CMDS` 사전(이름 → 함수)을 두면 여기 명령에 더해진다. 응답 완료 판정은 아래 `TurnJudge`를 가져다 쓴다.
처음 만든 곳: usroom tools/phone (2026-11-10, 검토 17차 AE2) → 2026-11-11 하네스 모듈로 일반화.
"""
import base64
import collections
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CONFIG = HERE / "phone.json"
DENY = HERE / "deny.txt"
ADB_IME = "com.android.adbkeyboard/.AdbIME"
LAUNCHERS = ("com.sec.android.app.launcher", "com.google.android.apps.nexuslauncher", "com.android.launcher")
STORES = ("com.android.vending",)
POLL = 1.5          # 응답 완료 확인 간격(초)
STABLE_N = 3        # 같은 목록이 이만큼 연속이면 완료

_conf = None


class Denied(Exception):
    pass


def conf():
    """phone.json — serial(비우면 adb 기본 기기)·app(패키지)·app_name·display_id(비우면 자동)·launchers(더할 런처)."""
    global _conf
    if _conf is None:
        _conf = json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
    return _conf


def serial():
    return os.environ.get("PHONE_SERIAL") or conf().get("serial") or ""


def app():
    return conf().get("app") or ""


def app_name():
    return conf().get("app_name") or app() or "앱"


# ---------- 순수 로직 (test_phone.py) ----------

def load_deny(path=None):
    p = Path(path) if path else DENY
    if not p.exists():
        raise FileNotFoundError(f"누르지 않는 목록 없음: {p} — 목록 없이는 탭하지 않는다")
    return [l.strip() for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.lstrip().startswith("#")]


def is_denied(strings, deny):
    for s in strings:
        if not s:
            continue
        for d in deny:
            if d in s:
                return d
    return None


def new_texts(before, after):
    """보내기 전보다 늘어난 텍스트(개수 기준 — 같은 문장이 또 생겨도 센다). 순서는 after 순서."""
    remain = collections.Counter(before)
    out = []
    for t in after:
        if remain[t] > 0:
            remain[t] -= 1
        else:
            out.append(t)
    return out


def reply_texts(before, after, sent, ignore=()):
    """늘어난 텍스트에서 보낸 문장 1개와 무시할 문구(입력란 안내 등)를 뺀 것."""
    out = [t for t in new_texts(before, after) if t not in ignore]
    if sent in out:
        out.remove(sent)
    return out


class TurnJudge:
    """늘어난 응답 목록이 stable_n회 연속 같으면 완료. fail_text가 보이면 실패.
    주의: 이전 글이 화면 밖으로 밀려나는 화면에선 '보낸 문장이 보이는가'를 확인 방법으로 쓰지 않는다(docs/phone-qa.md 4절)."""

    def __init__(self, before, sent, ignore=(), fail_text=None, stable_n=STABLE_N):
        self.before, self.sent, self.ignore = list(before), sent, tuple(ignore)
        self.fail_text, self.stable_n = fail_text, stable_n
        self.last, self.same = None, 0

    def feed(self, after):
        cur = reply_texts(self.before, after, self.sent, self.ignore)
        if self.fail_text and any(self.fail_text in t for t in cur):
            return "failed", cur
        if cur and cur == self.last:
            self.same += 1
        else:
            self.same = 1 if cur else 0
        self.last = cur
        return ("done" if self.same >= self.stable_n else "waiting"), cur


def wait_until(get, want, timeout, sleep=time.sleep, clock=time.monotonic, interval=5.0):
    """get()이 want와 같아질 때까지 기다린다. (성공 여부, 마지막 값)."""
    t0 = clock()
    while True:
        cur = get()
        if cur == want:
            return True, cur
        if clock() - t0 >= timeout:
            return False, cur
        sleep(interval)


def inside_repo(path, repo=REPO):
    p = Path(path).expanduser().resolve()
    try:
        p.relative_to(Path(repo).resolve())
        return True
    except ValueError:
        return False


def node_strings(n):
    return [n.get("text") or "", n.get("desc") or ""]


def dump_lines(nodes):
    """see --dump: 화면 트리의 글자 있는 노드를 위→아래 순서로. 누를 수 있는 것은 '•'."""
    rows = [n for n in nodes if (n.get("text") or n.get("desc"))]
    rows.sort(key=lambda n: (n.get("y", 0), n.get("x", 0)))
    out = []
    for n in rows:
        mark = "•" if n.get("clickable") else " "
        label = n.get("text") or ""
        if n.get("desc") and n.get("desc") != label:
            label = f"{label} [{n['desc']}]" if label else f"[{n['desc']}]"
        cls = (n.get("class") or "").rsplit(".", 1)[-1]
        out.append(f"{mark} {label}  ({cls} @{n.get('x')},{n.get('y')})")
    return out


# ---------- adb ----------

def adb_base():
    s = serial()
    return ["adb", "-s", s] if s else ["adb"]


def adb(*args, check=False, binary=False, timeout=30):
    r = subprocess.run([*adb_base(), *args], capture_output=True, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError(f"adb {' '.join(args)} 실패: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout if binary else r.stdout.decode(errors="replace")


def sh(cmd):
    return adb("shell", cmd)


def grep1(text, key):
    for line in text.splitlines():
        if key in line:
            return line.strip()
    return ""


def foreground():
    line = grep1(sh("dumpsys activity activities"), "topResumedActivity")
    # ...ActivityRecord{… u0 com.pkg/.Act t12}
    for tok in line.split():
        if "/" in tok:
            return tok.split("/")[0]
    return ""


def current_ime():
    return sh("settings get secure default_input_method").strip()


def app_version(pkg=None):
    out = sh(f"dumpsys package {pkg or app()}")
    vn = grep1(out, "versionName=").replace("versionName=", "")
    vc = grep1(out, "versionCode=").split(" ")[0].replace("versionCode=", "")
    return vn, vc


def main_display_id():
    """화면 둘인 폰(Flip 등)은 screencap 에 -d 가 필요하다. 설정 → 자동(HWC display 0) 순."""
    if conf().get("display_id"):
        return str(conf()["display_id"])
    for line in sh("dumpsys SurfaceFlinger --display-id").splitlines():
        if "HWC display 0" in line:
            return line.split()[1]
    return ""


# ---------- 명령: adb만 ----------

def _opt(args, name, default=None):
    if name in args:
        i = args.index(name)
        return args[i + 1] if i + 1 < len(args) else default
    return default


def cmd_preflight(args):
    """사용: preflight [--wait-version <versionName> [--timeout 초]]
    --wait-version: 그 버전이 깔릴 때까지 기다린 뒤 점검. 전면이 스토어(업데이트하던 화면)면 홈으로 돌려놓는다 — 그 밖의 전면 앱은 묻는다."""
    if not app():
        print(f"phone.json 의 app(패키지)이 비어 있음 — {CONFIG} 를 채워 주세요")
        return 2
    state = subprocess.run([*adb_base(), "get-state"], capture_output=True, text=True)
    st = (state.stdout or state.stderr).strip()
    print(f"기기: {serial() or '(기본)'} {st}")
    if st != "device":
        print("→ 폰 화면에서 'USB 디버깅 허용'을 눌러 주세요(사용자). unauthorized는 세션이 바뀌면 나온다. 기기가 여럿이면 phone.json serial.")
        return 2
    want = _opt(args, "--wait-version")
    if want:
        timeout = float(_opt(args, "--timeout", "600"))
        print(f"{app_name()} {want} 대기(최대 {timeout:.0f}초)…", flush=True)
        ok, got = wait_until(lambda: app_version()[0], want, timeout)
        if not ok:
            print(f"✗ 버전 대기 시간 초과 — 지금 {got or '미설치'}")
            return 1
        if foreground().startswith(STORES):
            sh("input keyevent KEYCODE_HOME")
            time.sleep(1.0)
            print("전면이 스토어였음 → 홈으로")
    bad = []
    fg = foreground()
    print(f"전면 앱: {fg or '?'}")
    launchers = LAUNCHERS + tuple(conf().get("launchers", []))
    if not (fg == app() or fg.startswith(launchers)):
        bad.append(f"전면 앱이 런처·{app_name()}이 아님(사용자가 폰을 쓰는 중일 수 있음 — 묻고 진행)")
    awake = "Awake" in grep1(sh("dumpsys power"), "mWakefulness=")
    locked = "isKeyguardShowing=true" in sh("dumpsys window")
    print(f"화면: {'켜짐' if awake else '꺼짐'} · 잠금: {'잠김' if locked else '풀림'}")
    if not awake or locked:
        bad.append("화면 꺼짐 또는 잠김(사용자가 풀어야 함 — PIN 입력 금지)")
    net = grep1(sh("dumpsys connectivity"), "Active default network")
    online = bool(net) and not net.endswith("none")
    print(f"네트워크: {'연결됨' if online else '없음'} ({net or '?'})")
    if not online:
        bad.append("네트워크 없음(Wi-Fi 연결 필요)")
    vn, vc = app_version()
    print(f"{app_name()}: {vn + ' (' + vc + ')' if vn else '미설치'}")
    if not vn:
        bad.append(f"{app_name()} 미설치")
    elif want and vn != want:
        bad.append(f"버전이 {want} 아님")
    print(f"키보드: {current_ime()}")
    for b in bad:
        print(f"✗ {b}")
    return 1 if bad else 0


def cmd_shot(args):
    if len(args) != 1:
        print("사용: shot <파일.png> (저장소 밖)")
        return 2
    if inside_repo(args[0]):
        print(f"거부: 저장소 안 경로({args[0]}) — 스크린샷은 스크래치패드 등 저장소 밖에 둔다")
        return 2
    d = main_display_id()
    png = adb("exec-out", "screencap", *(["-d", d] if d else []), "-p", binary=True, check=True)
    i = png.find(b"\x89PNG")   # 화면 둘인 폰은 'Multiple displays' 경고가 앞에 붙는다
    if i < 0:
        print("실패: PNG가 아님")
        return 1
    Path(args[0]).expanduser().write_bytes(png[i:])
    print(Path(args[0]).expanduser().resolve())
    return 0


# ---------- 명령: phone-harness 안에서 (h = 헬퍼 모음) ----------

def find(h, query, nodes=None):
    nodes = h["ui"]() if nodes is None else nodes
    return [n for n in nodes if any(query in s for s in node_strings(n))]


def safe_tap(h, query, deny=None):
    deny = load_deny() if deny is None else deny
    hit = is_denied([query], deny)
    if hit:
        raise Denied(f"누르지 않는 목록: '{hit}'")
    nodes = find(h, query)
    if not nodes:
        raise LookupError(f"화면에 '{query}' 없음")
    n = nodes[0]
    hit = is_denied(node_strings(n), deny)
    if hit:
        raise Denied(f"누르지 않는 목록: '{hit}' (노드 '{n.get('text') or n.get('desc')}')")
    h["tap"](n["x"], n["y"])
    return n


def edit_text(h):
    for n in h["ui"]():
        if n.get("class") == "android.widget.EditText":
            return n
    return None


def texts(h):
    return [n["text"] for n in h["ui"]() if n.get("class") == "android.widget.TextView" and n.get("text")]


def cmd_see(h, args):
    nodes = h["ui"]()
    if "--dump" in args:
        for line in dump_lines(nodes):
            print(line)
        return 0
    absent = "--absent" in args
    phrases = [a for a in args if a != "--absent"]
    if not phrases:
        print("사용: see [--absent] \"문구\" … | see --dump")
        return 2
    ok = True
    for p in phrases:
        found = find(h, p, nodes)
        for n in found:
            print(f"✓ '{p}' ← {n.get('text') or n.get('desc')!r} @({n['x']},{n['y']} {n['w']}x{n['h']})")
        if not found:
            print(f"✗ '{p}' 없음")
        ok = ok and (not found if absent else bool(found))
    return 0 if ok else 1


def cmd_tap(h, args):
    if len(args) != 1:
        print("사용: tap \"문구\"")
        return 2
    try:
        n = safe_tap(h, args[0])
    except Denied as e:
        print(f"거부: {e}")
        return 3
    except FileNotFoundError as e:
        print(f"거부: {e}")
        return 3
    except LookupError as e:
        print(f"실패: {e}")
        return 1
    h["wait_stable"](timeout=6)
    print(f"탭: {n.get('text') or n.get('desc')!r}")
    return 0


def type_ko(h, sentence):
    """ADBKeyboard로 입력하고 입력란을 대조. 성공·실패와 무관하게 원래 키보드로 되돌린다."""
    if ADB_IME not in sh("ime list -s"):
        raise RuntimeError("ADBKeyboard가 활성화돼 있지 않음 — docs/phone-qa.md '설치'(사용자 허락 뒤)")
    field = edit_text(h)
    if field is None:
        raise LookupError("입력란(EditText)이 화면에 없음")
    original = current_ime()
    try:
        h["tap"](field["x"], field["y"])          # 입력란 포커스(누르지 않는 목록 대상 아님)
        sh(f"ime set {ADB_IME}")
        time.sleep(1.0)
        sh("am broadcast -a ADB_CLEAR_TEXT")
        b64 = base64.b64encode(sentence.encode("utf-8")).decode()
        sh(f"am broadcast -a ADB_INPUT_B64 --es msg {b64}")
        time.sleep(0.8)
        got = (edit_text(h) or {}).get("text", "")
        if got != sentence:
            raise AssertionError(f"입력란 불일치: 기대 {sentence!r} / 실제 {got!r}")
        return got
    finally:
        sh(f"ime set {original}")
        after = current_ime()
        if after != original:
            print(f"경고: 키보드 복귀 실패 — 지금 {after}, 원래 {original}", file=sys.stderr)


def cmd_type_ko(h, args):
    if len(args) != 1:
        print("사용: type_ko \"문장\"")
        return 2
    try:
        print(f"입력: {type_ko(h, args[0])!r}")
        return 0
    except Exception as e:
        print(f"실패: {e}")
        return 1


HARNESS_CMDS = {"see": cmd_see, "tap": cmd_tap, "type_ko": cmd_type_ko}
ADB_CMDS = {"preflight": cmd_preflight, "shot": cmd_shot}


def load_app():
    """프로젝트의 tools/phone/app.py(있으면) — HARNESS_CMDS·ADB_CMDS 를 더한다."""
    p = HERE / "app.py"
    if not p.exists():
        return {}, {}
    spec = importlib.util.spec_from_file_location("phone_app", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "HARNESS_CMDS", {}), getattr(mod, "ADB_CMDS", {})


def commands():
    ah, aa = load_app()
    return {**HARNESS_CMDS, **ah}, {**ADB_CMDS, **aa}


def run_in_harness(cmd, args, g):
    """phone-harness가 exec하는 스크립트에서 부른다. g = 그 스크립트의 globals(헬퍼)."""
    h = {k: g[k] for k in ("ui", "tap", "open_app", "wait_stable")}
    return commands()[0][cmd](h, args)


def main(argv):
    hc, ac = commands()
    if not argv or argv[0] not in {**hc, **ac}:
        print(f"명령: {', '.join([*ac, *hc])}")
        return 2
    cmd, args = argv[0], argv[1:]
    if cmd in ac:
        return ac[cmd](args)
    script = (f"import sys, json\nsys.path.insert(0, {str(HERE)!r})\nimport phonelib\n"
              f"sys.exit(phonelib.run_in_harness({cmd!r}, json.loads({json.dumps(json.dumps(args))}), globals()))\n")
    return subprocess.run(["phone-harness"], input=script, text=True).returncode


if __name__ == "__main__":
    # app.py 가 `import phonelib` 해도 같은 모듈을 쓰게 이름으로 다시 불러 실행한다
    sys.path.insert(0, str(HERE))
    import phonelib
    sys.exit(phonelib.main(sys.argv[1:]))
