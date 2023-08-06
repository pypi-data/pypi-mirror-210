import argparse
import dataclasses
import json
import signal
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, List

import requests

from .exceptions import CheckWarning, UrlWarning, ResponseWarning, TimestampWarning, StatusWarning, ExpectedModesWarning, DictionaryError, StatusError, WarningTimeoutError

REQUEST_TIMEOUT_DEFAULT: float = 3.05  # see https://docs.python-requests.org/en/master/user/advanced/#timeouts
STAYINALIVE_TIMEOUT_DEFAULT: float = 15
WARNING_TIMEOUT_DEFAULT: float = 600  # 10 minutes
DELAY_DEFAULT: float = 3


@dataclasses.dataclass
class RemoteData:
    timestamp: datetime
    status: str
    mode: str

    def to_json(self):
        return json.dumps(dataclasses.asdict(self), indent=2, default=lambda obj: obj.isoformat())


def _response_from_url(url: str, request_timeout: float = REQUEST_TIMEOUT_DEFAULT, ignore_tls: bool = False) -> str:
    try:
        response = requests.get(url, timeout=request_timeout, verify=not ignore_tls)
        response.raise_for_status()
        return response.text
    except Exception as exception:
        raise UrlWarning(url, request_timeout) from exception


def _dictionary_from_response(response: str) -> dict:
    try:
        return json.loads(response)
    except Exception as exception:
        raise ResponseWarning(response) from exception


def _remote_data_from_dictionary(dictionary: dict) -> RemoteData:
    try:
        return RemoteData(datetime.fromisoformat(dictionary["timestamp"]), str(dictionary["status"]), str(dictionary["mode"]))
    except Exception as exception:
        raise DictionaryError(dictionary) from exception


def _check_timestamp(timestamp: datetime, stayinalive_timeout: float = STAYINALIVE_TIMEOUT_DEFAULT, now: datetime = None) -> None:
    if not now:
        now = datetime.fromtimestamp(time.time(), timezone.utc)

    if now - timestamp > timedelta(seconds=stayinalive_timeout):
        raise TimestampWarning(timestamp, stayinalive_timeout, now)


def _check_status(status: str) -> None:
    if status == "fixing":
        raise StatusWarning()
    elif status != "ok":
        raise StatusError(status)


def check(url: str, request_timeout: float = REQUEST_TIMEOUT_DEFAULT, stayinalive_timeout: float = STAYINALIVE_TIMEOUT_DEFAULT, ignore_tls: bool = False) -> RemoteData:
    response = _response_from_url(url, request_timeout, ignore_tls)
    dictionary = _dictionary_from_response(response)
    remote_data = _remote_data_from_dictionary(dictionary)
    _check_status(remote_data.status)
    _check_timestamp(remote_data.timestamp, stayinalive_timeout)

    return remote_data


def warning_tolerant_check(url: str,
                           event: threading.Event = None,
                           expected_modes: List[str] = None,
                           delay: float = DELAY_DEFAULT,
                           warning_timeout: float = WARNING_TIMEOUT_DEFAULT,
                           request_timeout: float = REQUEST_TIMEOUT_DEFAULT,
                           stayinalive_timeout: float = STAYINALIVE_TIMEOUT_DEFAULT,
                           ignore_tls: bool = False) -> RemoteData:
    if not event:
        event = threading.Event()

    timer = threading.Timer(warning_timeout, lambda: event.set())
    timer.start()

    try:
        while True:
            try:
                remote_data = check(url, request_timeout, stayinalive_timeout, ignore_tls)
                if not expected_modes or remote_data.mode in expected_modes:
                    return remote_data
                else:
                    raise ExpectedModesWarning(expected_modes)
            except CheckWarning as warning:
                event.wait(delay)
                if event.is_set():
                    raise WarningTimeoutError(warning)
    finally:
        timer.cancel()


def main(args: Optional[List[str]] = None) -> None:
    argparser = argparse.ArgumentParser(description="")
    argparser.add_argument("url", help="", metavar="<url>")
    argparser.add_argument("-m", "--expected-mode", action="append", dest="expected_modes", help="", metavar="<mode>")
    argparser.add_argument("-d", "--delay", type=float, default=DELAY_DEFAULT, help="", metavar="<duration>")
    argparser.add_argument("-w", "--warning-timeout", type=float, default=WARNING_TIMEOUT_DEFAULT, help="", metavar="<duration>")
    argparser.add_argument("-r", "--request-timeout", type=float, default=REQUEST_TIMEOUT_DEFAULT, help="", metavar="<duration>")
    argparser.add_argument("-t", "--stayinalive-timeout", type=float, default=STAYINALIVE_TIMEOUT_DEFAULT, help="", metavar="<duration>")
    argparser.add_argument("-i", "--ignore-tls", action="store_true", help="")
    args = argparser.parse_args(args)

    # turning SIGINT and SIGTERM into an event
    event = threading.Event()
    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, lambda signum, frame: event.set())

    print(warning_tolerant_check(args.url, event, args.expected_modes, args.delay, args.warning_timeout, args.request_timeout, args.stayinalive_timeout, args.ignore_tls).to_json())
