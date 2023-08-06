import pytest

import whassup


def test_none():
    with pytest.raises(whassup.ResponseWarning) as excinfo:
        whassup._dictionary_from_response(None)

    assert repr(excinfo.value.__cause__) == "TypeError('the JSON object must be str, bytes or bytearray, not NoneType')"


def test_plain_text():
    with pytest.raises(whassup.ResponseWarning) as excinfo:
        whassup._dictionary_from_response("lorem ipsum")

    assert excinfo.value.response == "lorem ipsum"
    assert repr(excinfo.value.__cause__) == "JSONDecodeError('Expecting value: line 1 column 1 (char 0)')"


def test_ok():
    assert whassup._dictionary_from_response('{"lorem": "ipsum"}') == {"lorem": "ipsum"}
