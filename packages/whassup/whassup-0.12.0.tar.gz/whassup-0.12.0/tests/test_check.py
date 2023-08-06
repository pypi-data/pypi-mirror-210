import datetime
import http.server
import json

import pytest
import time

import whassup


def test_ok(server):
    now = datetime.datetime.fromtimestamp(time.time(), datetime.timezone.utc)

    class Ok(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "timestamp": now.isoformat(),
                "status": "ok",
                "mode": "alpha"
            }).encode("utf-8"))

    server.RequestHandlerClass = Ok

    assert whassup.check("http://127.0.0.1:8000") == whassup.RemoteData(now, "ok", "alpha")


def test_old_ko(server):
    class OldKo(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "timestamp": "2000-01-01T00:00:00.000000+00:00",
                "status": "ko",
                "mode": "alpha"
            }).encode("utf-8"))

    server.RequestHandlerClass = OldKo

    with pytest.raises(whassup.exceptions.StatusError):
        whassup.check("http://127.0.0.1:8000")
