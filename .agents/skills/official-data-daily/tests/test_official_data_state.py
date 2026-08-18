import argparse
import copy
import datetime as dt
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "official_data_state.py"
SPEC = importlib.util.spec_from_file_location("official_data_state", SCRIPT)
STATE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(STATE)


class OfficialDataStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.root = Path(self.temp_dir.name) / "runtime"
        self.root.mkdir(parents=True)
        self.datasets = [
            {
                "dataset_id": "window-data",
                "name": "Window data",
                "institution": "Official institution",
                "release_url": "https://example.gov/window",
                "official_domain": "example.gov",
                "check_policy": {"mode": "window", "day_windows": [[10, 15]]},
            },
            {
                "dataset_id": "weekly-data",
                "name": "Weekly data",
                "institution": "Official institution",
                "release_url": "https://example.gov/weekly",
                "official_domain": "example.gov",
                "check_policy": {"mode": "weekly", "weekdays": [0]},
            },
            {
                "dataset_id": "interval-data",
                "name": "Interval data",
                "institution": "Official institution",
                "release_url": "https://example.gov/interval",
                "official_domain": "example.gov",
                "check_policy": {"mode": "interval", "interval_days": 7, "months": [2, 3]},
            },
            {
                "dataset_id": "calendar-data",
                "name": "Calendar data",
                "institution": "Official institution",
                "release_url": "https://example.gov/calendar",
                "official_domain": "example.gov",
                "calendar_url": "https://example.gov/schedule",
                "check_policy": {"mode": "calendar"},
            },
        ]
        self.write_json(self.root / "sources.json", {"datasets": self.datasets})
        STATE.command_init(argparse.Namespace(root=str(self.root)))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def write_json(path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def write_state(self, checked_at: dict[str, str]) -> None:
        state = STATE.initial_state()
        state["datasets"] = {
            dataset_id: {"last_checked_at": timestamp}
            for dataset_id, timestamp in checked_at.items()
        }
        self.write_json(self.root / "state" / "state.json", state)

    def plan(self, date: str) -> dict:
        return STATE.command_plan(argparse.Namespace(root=str(self.root), date=date))

    def test_missed_policy_dates_are_caught_up_once(self) -> None:
        self.write_state({
            "window-data": "2026-08-01T08:00:00+08:00",
            "weekly-data": "2026-08-09T08:00:00+08:00",
            "interval-data": "2026-01-25T08:00:00+08:00",
        })

        due = {item["dataset_id"]: item for item in self.plan("2026-08-16")["due_datasets"]}

        self.assertIn("window-data", due)
        self.assertIn("weekly-data", due)
        self.assertIn("interval-data", due)
        self.assertEqual(
            due["window-data"]["scan_window"]["start_exclusive"],
            "2026-08-01T08:00:00+08:00",
        )
        scan_end = dt.datetime.fromisoformat(
            due["window-data"]["scan_window"]["end_inclusive"]
        )
        target = dt.date(2026, 8, 16)
        self.assertEqual(scan_end.date(), target)
        if target != dt.datetime.now().astimezone().date():
            self.assertEqual(scan_end.time().replace(tzinfo=None), dt.time(23, 59, 59))

        self.write_state({"window-data": "2026-08-16T09:00:00+08:00"})
        due_ids = {item["dataset_id"] for item in self.plan("2026-08-17")["due_datasets"]}
        self.assertNotIn("window-data", due_ids)

    def test_missing_watermark_requires_one_time_baseline_outside_normal_window(self) -> None:
        self.write_state({})

        plan = self.plan("2026-08-16")
        due = {item["dataset_id"]: item for item in plan["due_datasets"]}

        self.assertEqual(set(due), {item["dataset_id"] for item in self.datasets})
        self.assertTrue(all(item["baseline_required"] for item in due.values()))
        self.assertTrue(all(item["scan_window"]["start_exclusive"] is None for item in due.values()))
        calendar_source = next(item for item in plan["calendar_sources"] if item["dataset_id"] == "calendar-data")
        self.assertTrue(calendar_source["baseline_required"])

    def test_missed_calendar_event_remains_due(self) -> None:
        self.write_state({"calendar-data": "2026-08-01T08:00:00+08:00"})
        self.write_json(self.root / "schedule.json", {
            "refreshed_at": "2026-08-10T09:00:00+08:00",
            "covered_datasets": ["calendar-data"],
            "events": [{
                "dataset_id": "calendar-data",
                "expected_at": "2026-08-10T09:30:00+08:00",
                "window_start": "2026-08-10",
                "window_end": "2026-08-11",
                "reference_period": "2026-07",
                "calendar_url": "https://example.gov/schedule",
            }],
        })

        due = {item["dataset_id"]: item for item in self.plan("2026-08-16")["due_datasets"]}

        self.assertEqual(due["calendar-data"]["schedule_events"][0]["reference_period"], "2026-07")

    def test_calendar_event_waits_for_expected_time_then_becomes_due_same_day(self) -> None:
        event = {
            "expected_at": "2026-08-10T09:30:00+08:00",
            "window_start": "2026-08-10",
            "window_end": "2026-08-11",
        }
        last_checked = "2026-08-10T07:00:00+08:00"

        self.assertFalse(STATE.event_is_due(
            event,
            last_checked,
            dt.date(2026, 8, 10),
            dt.datetime.fromisoformat("2026-08-10T08:00:00+08:00"),
        ))
        self.assertTrue(STATE.event_is_due(
            event,
            last_checked,
            dt.date(2026, 8, 10),
            dt.datetime.fromisoformat("2026-08-10T10:00:00+08:00"),
        ))

    def test_error_does_not_advance_coverage_and_no_change_summary_is_written(self) -> None:
        self.write_state({"window-data": "2026-08-01T08:00:00+08:00"})
        run = {
            "date": "2026-08-16",
            "started_at": "2026-08-16T09:00:00+08:00",
            "coverage_end": "2026-08-16T09:00:05+08:00",
            "finished_at": "2026-08-16T09:05:00+08:00",
            "checked": [],
            "results": [],
            "summary": "本次官方来源访问失败，未形成新的数据判断。",
            "errors": [{"dataset_id": "window-data", "message": "timeout"}],
        }
        run_path = self.root / "run.json"
        self.write_json(run_path, run)

        STATE.command_finish(argparse.Namespace(root=str(self.root), input=str(run_path)))

        state = json.loads((self.root / "state" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["datasets"]["window-data"]["last_checked_at"], "2026-08-01T08:00:00+08:00")
        self.assertEqual(state["datasets"]["window-data"]["last_attempted_at"], run["finished_at"])
        report = (self.root / "daily" / "2026-08-16.md").read_text(encoding="utf-8")
        self.assertIn("## 今日判断", report)
        self.assertIn(run["summary"], report)

    def test_no_change_run_requires_summary(self) -> None:
        run = {
            "date": "2026-08-16",
            "started_at": "2026-08-16T09:00:00+08:00",
            "coverage_end": "2026-08-16T09:00:05+08:00",
            "finished_at": "2026-08-16T09:05:00+08:00",
            "checked": [],
            "results": [],
            "errors": [],
        }
        run_path = self.root / "run.json"
        self.write_json(run_path, run)

        with self.assertRaisesRegex(ValueError, "run.summary is required"):
            STATE.command_finish(argparse.Namespace(root=str(self.root), input=str(run_path)))

    def test_success_advances_only_to_declared_coverage_end(self) -> None:
        self.write_state({"window-data": "2026-08-01T08:00:00+08:00"})
        run = {
            "date": "2026-08-16",
            "started_at": "2026-08-16T09:00:00+08:00",
            "coverage_end": "2026-08-16T09:00:05+08:00",
            "finished_at": "2026-08-16T09:05:00+08:00",
            "checked": ["window-data"],
            "results": [{"dataset_id": "window-data", "status": "unchanged"}],
            "summary": "本次检查未发现新增或官方修订。",
            "errors": [],
        }
        run_path = self.root / "run.json"
        self.write_json(run_path, run)

        STATE.command_finish(argparse.Namespace(root=str(self.root), input=str(run_path)))

        state = json.loads((self.root / "state" / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["datasets"]["window-data"]["last_checked_at"], run["coverage_end"])
        self.assertEqual(state["datasets"]["window-data"]["last_attempted_at"], run["finished_at"])

    def test_changed_run_reuses_synthesis_headline_without_duplicate_summary(self) -> None:
        headline = "本次最重要的变化是指标回升，但仍需下一期确认。"
        run = {
            "date": "2026-08-16",
            "checked": ["window-data"],
            "results": [{"dataset_id": "window-data", "status": "new", "record_path": "record.md"}],
            "synthesis": {
                "headline": headline,
                "sections": [],
                "confidence": "medium",
            },
            "errors": [],
        }

        report = STATE.daily_markdown(run)

        self.assertEqual(report.count(headline), 1)

    def test_new_or_revised_record_requires_analysis_but_unchanged_does_not(self) -> None:
        record = {
            "dataset_id": "window-data",
            "reference_period": "2026-07",
            "published_at": "2026-08-10T09:00:00+08:00",
            "retrieved_at": "2026-08-16T09:00:00+08:00",
            "source_title": "Official release",
            "source_url": "https://example.gov/window/release",
            "values": [{"metric": "value", "value": 1, "unit": "index"}],
        }
        record_path = self.root / "record.json"
        self.write_json(record_path, record)
        args = argparse.Namespace(root=str(self.root), input=str(record_path))

        with self.assertRaisesRegex(ValueError, "record.analysis is required"):
            STATE.command_commit(args)

        analyzed = copy.deepcopy(record)
        analyzed["analysis"] = {
            "headline": "该指标为1。",
            "behavioral_readout": "当前数据只确认指标水平，尚不足以说明趋势。",
            "confidence": "medium",
        }
        self.write_json(record_path, analyzed)
        self.assertEqual(STATE.command_commit(args)["status"], "new")

        self.write_json(record_path, record)
        self.assertEqual(STATE.command_commit(args)["status"], "unchanged")


if __name__ == "__main__":
    unittest.main()
