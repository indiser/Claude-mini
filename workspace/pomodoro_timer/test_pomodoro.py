"""Headless tests for the pomodoro timer logic."""

import os
import tempfile
import unittest

from pomodoro import (
    DEFAULT_LONG_BREAK_EVERY,
    DEFAULT_WORK_MINUTES,
    LONG_BREAK,
    SHORT_BREAK,
    WORK,
    Pomodoro,
    format_time,
    load_settings,
    save_settings,
)


class PomodoroTests(unittest.TestCase):
    def setUp(self):
        self.timer = Pomodoro(
            work_minutes=1,
            short_break_minutes=1,
            long_break_minutes=1,
            long_break_every=2,
            auto_start_break=False,
            auto_start_work=False,
        )

    def run_phase(self, seconds):
        """Tick the timer `seconds` times and return the last event."""
        event = None
        for _ in range(seconds):
            event = self.timer.tick()
        return event

    def test_starts_with_a_full_focus_session(self):
        self.assertEqual(self.timer.phase, WORK)
        self.assertEqual(self.timer.remaining, 60)
        self.assertFalse(self.timer.running)
        self.assertEqual(self.timer.completed, 0)
        self.assertEqual(self.timer.sessions_in_set, 0)

    def test_paused_timer_does_not_count_down(self):
        self.assertIsNone(self.timer.tick())
        self.assertEqual(self.timer.remaining, 60)

    def test_toggle_starts_and_pauses(self):
        self.assertTrue(self.timer.toggle())
        self.assertTrue(self.timer.running)
        self.assertFalse(self.timer.toggle())
        self.assertFalse(self.timer.running)

    def test_tick_counts_down(self):
        self.timer.start()
        self.assertIsNone(self.timer.tick())
        self.assertEqual(self.timer.remaining, 59)

    def test_focus_session_ends_in_a_short_break(self):
        self.timer.start()
        self.assertEqual(self.run_phase(60), WORK)
        self.assertEqual(self.timer.phase, SHORT_BREAK)
        self.assertEqual(self.timer.remaining, 60)
        self.assertEqual(self.timer.completed, 1)
        self.assertEqual(self.timer.sessions_in_set, 1)
        self.assertFalse(self.timer.running)

    def test_breaks_can_start_automatically(self):
        self.timer.auto_start_break = True
        self.timer.start()
        self.run_phase(60)
        self.assertTrue(self.timer.running)

    def test_focus_sessions_can_start_automatically(self):
        self.timer.auto_start_break = True
        self.timer.auto_start_work = True
        self.timer.start()
        self.run_phase(60)  # focus
        self.run_phase(60)  # short break
        self.assertEqual(self.timer.phase, WORK)
        self.assertTrue(self.timer.running)

    def test_long_break_after_a_full_set(self):
        self.timer.auto_start_break = True
        self.timer.auto_start_work = True
        self.timer.start()
        self.run_phase(60)  # focus 1
        self.run_phase(60)  # short break
        self.assertEqual(self.timer.phase, WORK)
        self.run_phase(60)  # focus 2
        self.assertEqual(self.timer.phase, LONG_BREAK)
        self.assertEqual(self.timer.sessions_in_set, 2)
        self.assertEqual(self.timer.completed, 2)

    def test_long_break_starts_a_fresh_set(self):
        self.timer.auto_start_break = True
        self.timer.auto_start_work = True
        self.timer.start()
        self.run_phase(60)  # focus 1
        self.run_phase(60)  # short break
        self.run_phase(60)  # focus 2
        self.assertEqual(self.timer.phase, LONG_BREAK)
        self.run_phase(60)  # the long break
        self.assertEqual(self.timer.phase, WORK)
        self.assertEqual(self.timer.sessions_in_set, 0)
        self.assertEqual(self.timer.completed, 2)

    def test_skip_leaves_the_focus_phase(self):
        self.assertEqual(self.timer.skip(), WORK)
        self.assertEqual(self.timer.phase, SHORT_BREAK)
        self.assertEqual(self.timer.completed, 0)
        self.assertEqual(self.timer.sessions_in_set, 0)

    def test_skip_leaves_the_break_phase(self):
        self.timer.skip()
        self.assertEqual(self.timer.skip(), SHORT_BREAK)
        self.assertEqual(self.timer.phase, WORK)

    def test_skip_keeps_the_timer_running(self):
        self.timer.start()
        self.timer.skip()
        self.assertTrue(self.timer.running)

    def test_reset_clears_everything(self):
        self.timer.start()
        self.run_phase(60)
        self.timer.reset()
        self.assertEqual(self.timer.phase, WORK)
        self.assertEqual(self.timer.remaining, 60)
        self.assertEqual(self.timer.completed, 0)
        self.assertFalse(self.timer.running)

    def test_progress_grows_from_zero_to_one(self):
        self.assertEqual(self.timer.progress(), 0.0)
        self.timer.start()
        self.run_phase(30)
        self.assertAlmostEqual(self.timer.progress(), 0.5)
        self.run_phase(30)
        self.assertAlmostEqual(self.timer.progress(), 0.0)  # new phase started

    def test_apply_settings_keeps_the_phase(self):
        self.timer.start()
        self.run_phase(10)
        self.timer.apply_settings(work_minutes=5)
        self.assertEqual(self.timer.phase, WORK)
        self.assertEqual(self.timer.remaining, 50)
        self.assertTrue(self.timer.running)

    def test_apply_settings_clamps_a_longer_countdown(self):
        self.timer.apply_settings(work_minutes=1)
        self.timer.apply_settings(work_minutes=5)
        self.assertEqual(self.timer.remaining, 60)

    def test_long_break_every_is_at_least_one(self):
        timer = Pomodoro(long_break_every=0)
        self.assertEqual(timer.long_break_every, 1)

    def test_defaults(self):
        timer = Pomodoro()
        self.assertEqual(timer.work_minutes, DEFAULT_WORK_MINUTES)
        self.assertEqual(timer.long_break_every, DEFAULT_LONG_BREAK_EVERY)


class FormatTests(unittest.TestCase):
    def test_formats_minutes_and_seconds(self):
        self.assertEqual(format_time(0), "00:00")
        self.assertEqual(format_time(5), "00:05")
        self.assertEqual(format_time(65), "01:05")
        self.assertEqual(format_time(1500), "25:00")

    def test_negative_values_are_clamped(self):
        self.assertEqual(format_time(-10), "00:00")


class SettingsTests(unittest.TestCase):
    def test_missing_file_gives_defaults(self):
        settings = load_settings(os.path.join(tempfile.gettempdir(), "nope.json"))
        self.assertEqual(settings["work_minutes"], DEFAULT_WORK_MINUTES)

    def test_saved_settings_are_read_back(self):
        path = os.path.join(tempfile.mkdtemp(), "settings.json")
        values = {
            "work_minutes": 30,
            "short_break_minutes": 7,
            "long_break_minutes": 20,
            "long_break_every": 3,
            "auto_start_break": False,
            "auto_start_work": True,
        }
        save_settings(values, path)
        self.assertEqual(load_settings(path), values)

    def test_broken_file_gives_defaults(self):
        path = os.path.join(tempfile.mkdtemp(), "settings.json")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("not json")
        self.assertEqual(load_settings(path)["work_minutes"], DEFAULT_WORK_MINUTES)


if __name__ == "__main__":
    unittest.main()
