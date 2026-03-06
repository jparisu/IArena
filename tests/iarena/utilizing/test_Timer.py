"""Tests for timer utilities."""

from __future__ import annotations

import importlib

timer_module = importlib.import_module("iarena.utilizing.Timer")
Timer = timer_module.Timer


def test_timer_start_pause_reset_elapsed(monkeypatch) -> None:
    """Timer should accumulate elapsed time across start/pause cycles."""
    now = {"value": 10.0}

    def fake_time() -> float:
        return now["value"]

    monkeypatch.setattr(timer_module.time, "time", fake_time)

    timer = Timer(start_activated=True)
    assert timer.is_active is True
    assert timer.start_time == 10.0

    now["value"] = 12.5
    timer.pause()
    assert timer.is_active is False
    assert timer.elapsed_time == 2.5

    # Pausing while already paused should be a no-op.
    timer.pause()
    assert timer.elapsed_time == 2.5

    now["value"] = 20.0
    timer.start()
    assert timer.is_active is True
    assert timer.start_time == 20.0

    now["value"] = 23.0
    assert timer.elapsed() == 5.5

    # Starting while already active keeps the current start timestamp.
    timer.start()
    assert timer.start_time == 20.0

    now["value"] = 30.0
    timer.reset()
    assert timer.elapsed_time == 0.0
    assert timer.start_time == 30.0

    now["value"] = 31.25
    assert timer.elapsed() == 1.25


def test_timer_manual_inactive_and_missing_start_time_branches(monkeypatch) -> None:
    """Edge branches should not crash and should keep sane state."""
    monkeypatch.setattr(timer_module.time, "time", lambda: 100.0)

    timer = Timer(start_activated=False)
    assert timer.is_active is False
    assert timer.elapsed() == 0.0

    timer.is_active = True
    timer.start_time = None
    timer.elapsed_time = 7.0

    assert timer.elapsed() == 7.0
    timer.pause()
    assert timer.is_active is True
    assert timer.elapsed_time == 7.0
