"""Utility math helpers used in tests."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RunningAverage:
    """Compute a running average without storing all values."""

    total: float = 0.0
    count: int = 0

    def include(self, value: float) -> "RunningAverage":
        if self.count < 0:
            raise ValueError("count cannot be negative")
        return RunningAverage(self.total + value, self.count + 1)

    @property
    def average(self) -> float:
        if self.count == 0:
            return 0.0
        return self.total / self.count
