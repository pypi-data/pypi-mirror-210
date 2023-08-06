import pytest

import whassup


def test_ko():
    with pytest.raises(whassup.StatusError) as excinfo:
        whassup._check_status("ko")

    assert excinfo.value.status == "ko"


def test_warning():
    with pytest.raises(whassup.StatusWarning):
        whassup._check_status("fixing")


def test_ok():
    whassup._check_status("ok")


def test_error():
    with pytest.raises(whassup.StatusError) as excinfo:
        whassup._check_status("wrong status")

    assert excinfo.value.status == "wrong status"
