from __future__ import annotations

import time

import pytest

from iarena.utilizing.timing.Timer import Timer


def test_init_with_start_activated_true_starts_measuring_time() -> None:
    timer = Timer(start_activated=True)
    time.sleep(0.03)

    assert timer.elapsed() > 0.0


def test_start_resumes_elapsed_time_from_paused_state() -> None:
    timer = Timer(start_activated=False)
    time.sleep(0.02)
    before_start = timer.elapsed()

    timer.start()
    time.sleep(0.03)

    assert timer.elapsed() > before_start


def test_pause_stops_elapsed_time_growth() -> None:
    timer = Timer(start_activated=True)
    time.sleep(0.03)
    timer.pause()
    paused_elapsed = timer.elapsed()
    time.sleep(0.03)

    assert timer.elapsed() == pytest.approx(paused_elapsed, abs=0.01)


def test_reset_clears_elapsed_while_keeping_running_mode() -> None:
    timer = Timer(start_activated=True)
    time.sleep(0.03)
    timer.reset()
    time.sleep(0.03)

    assert timer.elapsed() >= 0.02


def test_elapsed_returns_non_negative_float_value() -> None:
    timer = Timer(start_activated=False)

    elapsed = timer.elapsed()

    assert isinstance(elapsed, float)
    assert elapsed >= 0.0
