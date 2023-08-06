import datetime
import threading

import pytest

import whassup
from whassup.exceptions import CheckError, CheckWarning, ExpectedModesWarning, WarningTimeoutError


def test_ok(monkeypatch):
    remote_data = whassup.RemoteData(datetime.datetime.fromtimestamp(0), "ok", "mode")

    monkeypatch.setattr(whassup, "check", lambda *_: remote_data)

    assert whassup.warning_tolerant_check("url") == remote_data
    assert whassup.warning_tolerant_check("url", None, ["mode"]) == remote_data


def test_error_untouched(monkeypatch):
    def mock(*_):
        raise CheckError

    monkeypatch.setattr(whassup, "check", mock)

    with pytest.raises(CheckError):
        whassup.warning_tolerant_check("url")


def test_timeout(monkeypatch):
    calls = 0

    def mock(*_):
        nonlocal calls
        calls = calls + 1
        raise CheckWarning

    monkeypatch.setattr(whassup, "check", mock)

    with pytest.raises(WarningTimeoutError) as excinfo:
        whassup.warning_tolerant_check("url", threading.Event(), None, 0.1, 0.25)

    assert isinstance(excinfo.value.warning, CheckWarning)
    assert calls == 3


def test_timeout_mode(monkeypatch):
    calls = 0

    def mock(*_):
        nonlocal calls
        calls = calls + 1
        return whassup.RemoteData(datetime.datetime.fromtimestamp(0), "ok", "alpha")

    monkeypatch.setattr(whassup, "check", mock)

    with pytest.raises(WarningTimeoutError) as excinfo:
        whassup.warning_tolerant_check("url", threading.Event(), ["beta", "gamma"], 0.1, 0.25)

    assert isinstance(excinfo.value.warning, ExpectedModesWarning)
    assert calls == 3


def test_warning_then_ok(monkeypatch):
    calls = 0
    remote_data = whassup.RemoteData(datetime.datetime.fromtimestamp(0), "ok", "mode")

    def mock(*_):
        nonlocal calls
        calls = calls + 1

        if calls < 3:
            raise CheckWarning
        else:
            return remote_data

    monkeypatch.setattr(whassup, "check", mock)

    assert whassup.warning_tolerant_check("url", threading.Event(), None, 0.1) == remote_data


def test_wait_for_mode(monkeypatch):
    calls = 0
    alpha = whassup.RemoteData(datetime.datetime.fromtimestamp(0), "ok", "alpha")
    beta = whassup.RemoteData(datetime.datetime.fromtimestamp(0), "ok", "beta")

    def mock(*_):
        nonlocal calls
        calls = calls + 1

        if calls == 1:
            raise CheckWarning
        elif calls == 2:
            return alpha
        else:
            return beta

    monkeypatch.setattr(whassup, "check", mock)

    assert whassup.warning_tolerant_check("url", threading.Event(), ["beta", "gamma"], 0.1) == beta


def test_event_externally_set(monkeypatch):
    calls = 0

    def mock(*_):
        nonlocal calls
        calls = calls + 1
        raise CheckWarning

    monkeypatch.setattr(whassup, "check", mock)

    event = threading.Event()

    timer = threading.Timer(0.25, lambda: event.set())
    timer.start()

    with pytest.raises(WarningTimeoutError):
        whassup.warning_tolerant_check("url", event, None, 0.1)

    assert calls == 3
