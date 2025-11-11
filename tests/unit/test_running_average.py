import pytest

from services.test_support.simple_math import RunningAverage


def test_running_average_accumulates_values():
    avg = RunningAverage()
    avg = avg.include(10)
    avg = avg.include(20)
    avg = avg.include(30)

    assert avg.total == 60
    assert avg.count == 3
    assert avg.average == 20


def test_running_average_zero_count_returns_zero():
    avg = RunningAverage()
    assert avg.average == 0


def test_running_average_negative_count_guard():
    avg = RunningAverage(total=10, count=-1)
    with pytest.raises(ValueError):
        avg.include(5)
