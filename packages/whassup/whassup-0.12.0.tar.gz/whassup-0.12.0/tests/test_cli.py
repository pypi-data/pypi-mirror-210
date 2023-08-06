import datetime
import os
import signal
import threading
import time

import pytest

import whassup


def mock(url, event, modes, delay, warning_timeout, request_timeout, stayinalive_timeout, ignore_tls):
    print(url, modes, delay, warning_timeout, request_timeout, stayinalive_timeout, ignore_tls)

    event.wait(0.5)
    if event.is_set():
        return whassup.RemoteData(datetime.datetime.fromtimestamp(0), "ok", "alpha")


def delayed_kill():
    time.sleep(0.2)
    os.kill(os.getpid(), signal.SIGINT)


@pytest.fixture(autouse=True)
def setup(monkeypatch):
    monkeypatch.setattr(whassup, "warning_tolerant_check", mock)
    threading.Thread(target=delayed_kill).start()


OK_OUTPUT = """
url ['alpha'] 0.1 0.2 0.3 0.4 True
{
  "timestamp": "1970-01-01T01:00:00",
  "status": "ok",
  "mode": "alpha"
}
""".lstrip()


def test_ok(capsys):
    whassup.main(["url", "-m", "alpha", "-d", "0.1", "-w", "0.2", "-r", "0.3", "-t", "0.4", "-i"])

    assert capsys.readouterr().out == OK_OUTPUT


OK_DEFAULT_VALUES_OUTPUT = """
url None 3 600 3.05 15 False
{
  "timestamp": "1970-01-01T01:00:00",
  "status": "ok",
  "mode": "alpha"
}
""".lstrip()


def test_ok_default_values(capsys):
    whassup.main(["url"])

    assert capsys.readouterr().out == OK_DEFAULT_VALUES_OUTPUT


def test_ko_missing_url(capsys):
    with pytest.raises(SystemExit) as excinfo:
        whassup.main([])

    assert excinfo.value.code == 2
    assert "error: the following arguments are required: <url>" in capsys.readouterr().err
