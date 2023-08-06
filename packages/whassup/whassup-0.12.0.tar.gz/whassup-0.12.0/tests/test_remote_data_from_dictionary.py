from datetime import datetime

import pytest

import whassup


def test_none():
    with pytest.raises(whassup.DictionaryError) as excinfo:
        whassup._remote_data_from_dictionary(None)

    assert repr(excinfo.value.__cause__) == """TypeError("'NoneType' object is not subscriptable")"""


def test_empty():
    with pytest.raises(whassup.DictionaryError) as excinfo:
        whassup._remote_data_from_dictionary({})

    assert excinfo.value.dictionary == {}
    assert repr(excinfo.value.__cause__) == "KeyError('timestamp')"


def test_bad_timestamp():
    with pytest.raises(whassup.DictionaryError) as excinfo:
        whassup._remote_data_from_dictionary({"timestamp": "MCMLXXXIV"})

    assert repr(excinfo.value.__cause__) == """ValueError("Invalid isoformat string: 'MCMLXXXIV'")"""


def test_missing_status():
    with pytest.raises(whassup.DictionaryError) as excinfo:
        whassup._remote_data_from_dictionary({"timestamp": "1970-01-01T00:00:00+00:00"})

    assert repr(excinfo.value.__cause__) == "KeyError('status')"


def test_missing_modes():
    with pytest.raises(whassup.DictionaryError) as excinfo:
        whassup._remote_data_from_dictionary({
            "timestamp": "1970-01-01T00:00:00+00:00",
            "status": "ok"
        })

    assert repr(excinfo.value.__cause__) == "KeyError('mode')"


def test_ok():
    assert whassup._remote_data_from_dictionary({
        "timestamp": "1970-01-01T00:00:00+00:00",
        "status": "ok",
        "mode": "alpha"
    }) == whassup.RemoteData(datetime.fromisoformat("1970-01-01T00:00:00+00:00"), "ok", "alpha")
