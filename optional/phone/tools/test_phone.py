"""폰 없이 도는 공용 헬퍼 테스트 — python3 -m unittest tools/phone/test_phone.py
하네스 optional/phone 공용 파일. 프로젝트 고유(deny.txt 문구·app.py 명령) 테스트는 프로젝트가 따로 둔다(예: test_app.py)."""
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import phonelib as pl  # noqa: E402

DENY = ["결제하기", "탈퇴하기", "로그아웃", "계정과 기기의 기록을 모두 지워요"]


def node(text="", desc="", cls="android.widget.TextView", x=10, y=20, clickable=True):
    return {"text": text, "desc": desc, "id": "", "class": cls, "clickable": clickable,
            "x": x, "y": y, "w": 5, "h": 5}


class FakeHarness:
    def __init__(self, screens):
        self.screens = list(screens)   # ui()가 차례로 돌려줄 노드 목록들(마지막은 반복)
        self.taps = []

    def ui(self):
        return self.screens[0] if len(self.screens) == 1 else self.screens.pop(0)

    def tap(self, x, y):
        self.taps.append((x, y))

    def h(self):
        return {"ui": self.ui, "tap": self.tap, "open_app": lambda _: None,
                "wait_stable": lambda **_: True}


class DenyTest(unittest.TestCase):
    def test_load_deny_skips_comments_and_blanks(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "deny.txt"
            p.write_text("# 설명\n결제하기\n\n  로그아웃  \n", encoding="utf-8")
            self.assertEqual(pl.load_deny(p), ["결제하기", "로그아웃"])

    def test_missing_deny_file_refuses(self):
        with self.assertRaises(FileNotFoundError):
            pl.load_deny(Path(tempfile.gettempdir()) / "없는-deny.txt")

    def test_query_in_deny_list_is_refused_without_tapping(self):
        fake = FakeHarness([[node("결제하기")]])
        with self.assertRaises(pl.Denied):
            pl.safe_tap(fake.h(), "결제하기", DENY)
        self.assertEqual(fake.taps, [])

    def test_partial_query_hitting_denied_node_is_refused(self):
        # '결제'만 요청해도 실제로 잡힌 노드가 결제 버튼이면 거부
        fake = FakeHarness([[node("결제하기")]])
        with self.assertRaises(pl.Denied):
            pl.safe_tap(fake.h(), "결제", DENY)
        self.assertEqual(fake.taps, [])

    def test_denied_content_description_is_refused(self):
        fake = FakeHarness([[node(desc="로그아웃")]])
        with self.assertRaises(pl.Denied):
            pl.safe_tap(fake.h(), "로그아웃", DENY)
        self.assertEqual(fake.taps, [])

    def test_row_description_is_refused_even_partially(self):
        phrase = "계정과 기기의 기록을 모두 지워요"
        fake = FakeHarness([[node(phrase)]])
        with self.assertRaises(pl.Denied):
            pl.safe_tap(fake.h(), phrase[:6], DENY)
        self.assertEqual(fake.taps, [])

    def test_allowed_button_is_tapped(self):
        fake = FakeHarness([[node(desc="보내기", x=900, y=1400)]])
        pl.safe_tap(fake.h(), "보내기", DENY)
        self.assertEqual(fake.taps, [(900, 1400)])

    def test_missing_text_is_lookup_error(self):
        fake = FakeHarness([[node("다른 것")]])
        with self.assertRaises(LookupError):
            pl.safe_tap(fake.h(), "보내기", DENY)


class SeeTest(unittest.TestCase):
    def run_see(self, nodes, args):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = pl.cmd_see(FakeHarness([nodes]).h(), args)
        return rc, buf.getvalue()

    def test_present_and_absent(self):
        nodes = [node("환불받을 수 있어요")]
        self.assertEqual(self.run_see(nodes, ["환불"])[0], 0)
        self.assertEqual(self.run_see(nodes, ["없는 문구"])[0], 1)
        self.assertEqual(self.run_see(nodes, ["--absent", "없는 문구"])[0], 0)
        self.assertEqual(self.run_see(nodes, ["--absent", "환불"])[0], 1)

    def test_dump_lists_text_top_to_bottom_with_clickable_mark(self):
        nodes = [node("아래", y=500, clickable=False), node(desc="보내기", y=900, cls="android.widget.Button"),
                 node("위", y=100, clickable=False), node("", y=50)]
        rc, out = self.run_see(nodes, ["--dump"])
        self.assertEqual(rc, 0)
        lines = out.strip().splitlines()
        self.assertEqual(len(lines), 3)              # 글자 없는 노드는 뺀다
        self.assertIn("위", lines[0])
        self.assertTrue(lines[2].startswith("• [보내기]"))
        self.assertIn("Button", lines[2])


class TurnJudgeTest(unittest.TestCase):
    BEFORE = ["상대", "들려?", "안녕", "말을 걸어보세요…"]

    def run_judge(self, sent, screens, **kw):
        j = pl.TurnJudge(self.BEFORE, sent, ignore=["말을 걸어보세요…"], **kw)
        states = [j.feed(s)[0] for s in screens]
        return states, j.last

    def test_single_reply_completes_after_three_same(self):
        after = self.BEFORE + ["오늘 피곤해", "그럼 좀 쉬어."]
        states, last = self.run_judge("오늘 피곤해", [after] * 3)
        self.assertEqual(states, ["waiting", "waiting", "done"])
        self.assertEqual(last, ["그럼 좀 쉬어."])

    def test_resending_same_sentence_counts_by_number(self):
        after = self.BEFORE + ["안녕", "또 왔네."]
        states, last = self.run_judge("안녕", [after] * 3)
        self.assertEqual(states[-1], "done")
        self.assertEqual(last, ["또 왔네."])

    def test_streaming_text_keeps_waiting_until_it_stops_growing(self):
        base = self.BEFORE + ["피곤해"]
        screens = [base + ["그럼"], base + ["그럼 좀"], base + ["그럼 좀 쉬어."],
                   base + ["그럼 좀 쉬어."], base + ["그럼 좀 쉬어."]]
        states, last = self.run_judge("피곤해", screens)
        self.assertEqual(states, ["waiting", "waiting", "waiting", "waiting", "done"])

    def test_only_user_bubble_is_not_done(self):
        states, last = self.run_judge("피곤해", [self.BEFORE + ["피곤해"]] * 5)
        self.assertNotIn("done", states)
        self.assertEqual(last, [])

    def test_failure_text_is_reported(self):
        after = self.BEFORE + ["피곤해", "대답이 돌아오지 않았다"]
        states, _ = self.run_judge("피곤해", [after], fail_text="대답이 돌아오지 않았다")
        self.assertEqual(states, ["failed"])

    def test_scrolled_off_old_text_does_not_count(self):
        after = self.BEFORE[1:] + ["피곤해", "쉬어."]
        _, last = self.run_judge("피곤해", [after] * 3)
        self.assertEqual(last, ["쉬어."])


class WaitTest(unittest.TestCase):
    def test_wait_until_reaches_value(self):
        vals = iter(["0.1.1", "0.1.1", "0.1.2"])
        t = [0.0]
        ok, got = pl.wait_until(lambda: next(vals), "0.1.2", 60, sleep=lambda s: t.__setitem__(0, t[0] + s),
                                clock=lambda: t[0])
        self.assertTrue(ok)
        self.assertEqual(got, "0.1.2")

    def test_wait_until_times_out(self):
        t = [0.0]
        ok, got = pl.wait_until(lambda: "0.1.1", "0.1.2", 12, sleep=lambda s: t.__setitem__(0, t[0] + s),
                                clock=lambda: t[0])
        self.assertFalse(ok)
        self.assertEqual(got, "0.1.1")


class PathTest(unittest.TestCase):
    def test_path_inside_repo_is_refused(self):
        self.assertTrue(pl.inside_repo(pl.REPO / "shot.png"))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(pl.cmd_shot([str(pl.REPO / "shot.png")]), 2)

    def test_path_outside_repo_is_allowed(self):
        self.assertFalse(pl.inside_repo(pl.REPO.parent / "other" / "x.png"))


class AppHookTest(unittest.TestCase):
    def test_app_py_adds_commands(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "app.py").write_text("HARNESS_CMDS = {'turn': lambda h, a: 0}\nADB_CMDS = {'reset': lambda a: 0}\n",
                                            encoding="utf-8")
            old = pl.HERE
            pl.HERE = Path(d)
            try:
                hc, ac = pl.commands()
            finally:
                pl.HERE = old
            self.assertIn("turn", hc)
            self.assertIn("see", hc)
            self.assertIn("reset", ac)
            self.assertIn("preflight", ac)


if __name__ == "__main__":
    unittest.main()
