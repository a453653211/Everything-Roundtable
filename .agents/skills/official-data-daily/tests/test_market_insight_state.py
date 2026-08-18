import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "market_insight_state.py"
SPEC = importlib.util.spec_from_file_location("market_insight_state", SCRIPT)
WATCH = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(WATCH)


class MarketInsightStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        WATCH.command_init(argparse.Namespace(root=str(self.root)))

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_input(self, name: str, data: dict) -> Path:
        path = self.root / name
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path

    def test_baseline_then_new_item_is_idempotent(self) -> None:
        plan = WATCH.command_plan(argparse.Namespace(root=str(self.root)))
        self.assertTrue(plan["baseline_required"])

        baseline = {
            "url": "https://www.citadelsecurities.com/news-and-insights/example/existing/",
            "title": "Existing",
            "series": "Series",
        }
        baseline_path = self.write_input("baseline.json", baseline)
        result = WATCH.command_commit(
            argparse.Namespace(
                root=str(self.root), input=str(baseline_path), baseline=True, seen_at="2026-08-16T07:00:00+08:00"
            )
        )
        self.assertEqual(result["status"], "baseline")

        finish_path = self.write_input(
            "finish.json",
            {
                "checked": True,
                "checked_at": "2026-08-16T07:01:00+08:00",
                "category_lastmod": "2026-08-12T04:05:03+00:00",
            },
        )
        WATCH.command_finish(argparse.Namespace(root=str(self.root), input=str(finish_path)))
        self.assertFalse(WATCH.command_plan(argparse.Namespace(root=str(self.root)))["baseline_required"])

        new = {
            "url": "https://www.citadelsecurities.com/news-and-insights/example/new-item/",
            "title": "New item",
            "published_at": "2026-08-17",
            "retrieved_at": "2026-08-17T07:00:00+08:00",
            "series": "Series",
            "author": "Author",
            "summary_zh": "核心判断。",
            "evidence": [{"fact": "具体数据。", "basis": "出版方平台数据"}],
            "forecasts": [{"claim": "方向判断。", "horizon": "一个月", "verification": "月末公开数据"}],
            "caveats": ["未独立验证"],
        }
        new_path = self.write_input("new.json", new)
        args = argparse.Namespace(root=str(self.root), input=str(new_path), baseline=False, seen_at=None)
        first = WATCH.command_commit(args)
        second = WATCH.command_commit(args)
        self.assertEqual(first["status"], "new")
        self.assertEqual(second["status"], "unchanged")
        self.assertTrue(Path(first["record_path"]).exists())

    def test_error_does_not_advance_successful_watermark(self) -> None:
        ok_path = self.write_input(
            "ok.json",
            {
                "checked": True,
                "checked_at": "2026-08-16T07:01:00+08:00",
                "category_lastmod": "2026-08-12T04:05:03+00:00",
            },
        )
        WATCH.command_finish(argparse.Namespace(root=str(self.root), input=str(ok_path)))
        error_path = self.write_input(
            "error.json",
            {"checked": False, "checked_at": "2026-08-17T07:01:00+08:00", "error": "category page unavailable"},
        )
        WATCH.command_finish(argparse.Namespace(root=str(self.root), input=str(error_path)))
        state = WATCH.load_state(self.root)
        self.assertEqual(state["last_successful_check"], "2026-08-16T07:01:00+08:00")
        self.assertEqual(state["category_lastmod"], "2026-08-12T04:05:03+00:00")
        self.assertEqual(state["last_attempted_at"], "2026-08-17T07:01:00+08:00")

    def test_rejects_non_citadel_url(self) -> None:
        bad = {"url": "https://example.com/article/", "title": "Bad"}
        bad_path = self.write_input("bad.json", bad)
        with self.assertRaises(ValueError):
            WATCH.command_commit(
                argparse.Namespace(root=str(self.root), input=str(bad_path), baseline=True, seen_at=None)
            )


if __name__ == "__main__":
    unittest.main()
