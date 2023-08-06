import time
from datetime import datetime, timezone, timedelta

import pytest

import whassup


@pytest.fixture
def now():
    return datetime.fromtimestamp(time.time(), timezone.utc)


def test_minimum_parameters(now):
    whassup._check_timestamp(now)


def test_warning(now):
    with pytest.raises(whassup.TimestampWarning) as excinfo:
        then = now - timedelta(seconds=2)
        whassup._check_timestamp(then, 1, now)

    assert excinfo.value.timestamp == then
    assert excinfo.value.stayinalive_timeout == 1
    assert excinfo.value.now == now


def test_ok(now):
    then = now - timedelta(seconds=1)
    whassup._check_timestamp(then, 2, now)
