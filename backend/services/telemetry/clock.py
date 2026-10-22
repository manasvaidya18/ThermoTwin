"""Demo clock: replays the scenario one 10-minute reading at a time."""
from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np


@dataclass
class Clock:
    start: int
    end: int
    tick: int = 0
    playing: bool = False
    seconds_per_tick: float = 2.0
    _t0: float = 0.0
    _tick0: int = 0

    def __post_init__(self) -> None:
        self.tick = self._tick0 = self.start

    def now(self) -> int:
        if self.playing:
            self.tick = min(self.end, self._tick0 + int((time.time() - self._t0) / self.seconds_per_tick))
        return self.tick

    def play(self) -> None:
        self._tick0, self._t0, self.playing = self.now(), time.time(), True

    def pause(self) -> None:
        self.now()
        self.playing = False

    def reset(self) -> None:
        self.playing, self.tick = False, self.start

    def step(self, ticks: int) -> None:
        self.tick = int(np.clip(self.now() + ticks, 0, self.end))
        self._tick0, self._t0 = self.tick, time.time()
