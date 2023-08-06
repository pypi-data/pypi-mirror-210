import datetime
import http.server
import ssl
import threading

import pytest
import time
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.x509.oid import NameOID

import whassup


def test_none():
    with pytest.raises(whassup.UrlWarning) as excinfo:
        whassup._response_from_url(None)

    assert repr(excinfo.value.__cause__) == """MissingSchema("Invalid URL 'None': No scheme supplied. Perhaps you meant https://None?")"""


def test_not_responding(server):
    server.RequestHandlerClass = None

    with pytest.raises(whassup.UrlWarning) as excinfo:
        whassup._response_from_url("http://127.0.0.1:8000")

    assert excinfo.value.url == "http://127.0.0.1:8000"
    assert excinfo.value.request_timeout == whassup.REQUEST_TIMEOUT_DEFAULT
    assert repr(excinfo.value.__cause__) == "ConnectionError(ProtocolError('Connection aborted.', RemoteDisconnected('Remote end closed connection without response')))"


def test_404(server):
    class NotFound(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(404)
            self.end_headers()

    server.RequestHandlerClass = NotFound

    with pytest.raises(whassup.UrlWarning) as excinfo:
        whassup._response_from_url("http://127.0.0.1:8000")

    assert repr(excinfo.value.__cause__) == "HTTPError('404 Client Error: Not Found for url: http://127.0.0.1:8000/')"


def test_request_timeout(server):
    class RequestTimeout(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            time.sleep(0.2)

    server.RequestHandlerClass = RequestTimeout

    with pytest.raises(whassup.UrlWarning) as excinfo:
        whassup._response_from_url("http://127.0.0.1:8000", 0.1)

    assert excinfo.value.request_timeout == 0.1
    assert repr(excinfo.value.__cause__) == """ReadTimeout(ReadTimeoutError("HTTPConnectionPool(host='127.0.0.1', port=8000): Read timed out. (read timeout=0.1)"))"""


class Ok(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write("lorem ipsum".encode("utf-8"))


def test_ok(server):
    server.RequestHandlerClass = Ok

    assert whassup._response_from_url("http://127.0.0.1:8000") == "lorem ipsum"


def test_ignore_tls(tmp_path):
    class TLSServer(http.server.ThreadingHTTPServer):
        def __init__(self):
            super().__init__(("0.0.0.0", 4443), Ok)

            key = rsa.generate_private_key(65537, 4096)
            cert = x509.CertificateBuilder() \
                .subject_name(name := x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])) \
                .issuer_name(name) \
                .public_key(key.public_key()) \
                .serial_number(x509.random_serial_number()) \
                .not_valid_before(now := datetime.datetime.utcnow()) \
                .not_valid_after(now + datetime.timedelta(days=10)) \
                .add_extension(x509.SubjectAlternativeName([x509.DNSName("localhost")]), critical=False) \
                .sign(key, hashes.SHA256())

            key_file, cert_file = tmp_path.joinpath("key.pem"), tmp_path.joinpath("cert.pem")
            key_file.write_bytes(key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()))
            cert_file.write_bytes(cert.public_bytes(Encoding.PEM))

            self.socket = ssl.wrap_socket(self.socket, keyfile=key_file, certfile=cert_file, server_side=True)

        def __enter__(self):
            threading.Thread(target=self.serve_forever).start()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.shutdown()
            self.server_close()

    with TLSServer():
        with pytest.raises(whassup.UrlWarning) as excinfo:
            whassup._response_from_url("https://127.0.0.1:4443")
        assert "CERTIFICATE_VERIFY_FAILED" in str(excinfo.value.__cause__)

        assert whassup._response_from_url("https://127.0.0.1:4443", ignore_tls=True) == "lorem ipsum"
