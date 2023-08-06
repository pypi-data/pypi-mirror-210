import io
import os
import subprocess
from logging import getLogger
from psutil import Process
from threading import Thread
import pytest
import signal
import sys
import time
import timeout_decorator
import traceback
from typing import (
    Any,
    Callable,
    cast,
    Dict,
    Iterable,
    Optional,
    Sequence,
    TextIO,
    Tuple,
)
from unittest import TestCase
import werkzeug
from werkzeug.datastructures import Headers
from werkzeug.test import Client
from werkzeug.wsgi import LimitedStream

from .subprocess_middleware import SubprocessMiddleware
from .wsgi_typing import (
    Environ,
    ExcInfo,
    StartResponse,
    WriteCallable,
)

# Used for testing that only gets initialized once in the forkserver
# process, and not once per spawned subprocess.
TEST_GLOBAL_VAR = os.getpid()

LOGGER = getLogger("pothead.test_subprocess_middleware")


def assertActiveException() -> ExcInfo:
    exc_info = sys.exc_info()
    assert exc_info[0] is not None
    assert exc_info[1] is not None
    assert exc_info[2] is not None
    return exc_info


# This function executes inside the spawned subprocess
def wrapped_app(environ: Environ, start_response: StartResponse) -> Iterable[bytes]:
    # Separate code path for tests that do not read request payload
    if environ["PATH_INFO"] == "/test_success_app_does_not_read_payload":
        start_response("200 OK", [], None)
        yield b"This is a successful response"
    else:
        request = werkzeug.Request(cast(Dict[str, Any], environ))
        assert request.is_multiprocess

        if request.path == "/test_success_with_request_and_response_payloads":
            assert request.data == b"Non-UTF8 binary payload: \x80"
            start_response("200 OK", [("key1", "value1"), ("key2", "value2")], None)
            yield b"This is a "
            yield b"non-UTF8 success response: \x80"
        elif request.path == "/test_success_with_payload_and_cpu_reservation_reset":
            start_response("200 OK", [], None)
            assert "RESET_CPU_RESERVATION" in environ
            reset_cpu_reservation = cast(
                Callable[[int], None], environ["RESET_CPU_RESERVATION"]
            )
            yield b"This is a "
            reset_cpu_reservation(7)
            yield b"successful response"
        elif (
            request.path == "/test_no_cpu_reservation_reset_if_none_in_original_request"
        ):
            assert "RESET_CPU_RESERVATION" not in environ
            start_response("200 OK", [], None)
            yield b"This is a successful response"
        elif request.path == "/test_success_with_no_response_payload":
            start_response("200 OK", [], None)
        elif request.path == "/test_failed_request_with_wsgi_error_output":
            wsgi_errors = cast(TextIO, environ.get("wsgi.errors"))
            wsgi_errors.write("First error output\n")
            start_response("500 Internal Server Error", [], None)
            wsgi_errors.write("Second error output\n")
        elif request.path == "/test_exception_raised_in_wrapped_app":

            def a_function_in_the_wrapped_app_callstack():
                raise Exception("This is an exception message")

            a_function_in_the_wrapped_app_callstack()
        elif request.path == "/test_exception_returned_from_start_response":

            def a_function_in_the_wrapped_app_callstack():
                try:
                    raise Exception("This is an exception message")
                except Exception:
                    exc_info = assertActiveException()
                    start_response(
                        "500 Internal Server Error",
                        [("key1", "value1"), ("key2", "value2")],
                        exc_info,
                    )

            a_function_in_the_wrapped_app_callstack()
        elif request.path == "/test_wrapped_app_dies_from_signal":
            os.kill(os.getpid(), signal.SIGKILL)
        elif request.path == "/test_globals_not_reinitialized_for_each_request":
            start_response("200 OK", [], None)
            yield f"TEST_GLOBAL_VAR: {TEST_GLOBAL_VAR}".encode("utf-8")
        elif request.path in [
            "/test_successful_subprocess_is_shut_down",
            "/test_failing_subprocess_is_shut_down",
        ]:

            def sleep_forever():
                while True:
                    time.sleep(1)

            # This thread will prevent the subprocess from exiting normally
            t = Thread(target=sleep_forever, daemon=False)
            t.start()

            # This subprocess represents something that the app might spawn, that doesn't automatically exit on its own
            subprocess.Popen(
                ["bash", "-c", "while true; do sleep 1000; echo HI FROM APP; done"]
            )

            if request.path == "/test_successful_subprocess_is_shut_down":
                start_response("200 OK", [], None)
            else:
                raise Exception("This is an exception message")
        elif request.path == "/test_client_disconnect_while_sending_request":
            raise Exception("Should never make it to this point")
        else:
            assert False, f"Unknown test endpoint path: {request.path}"


class SubprocessMiddlewareTest(TestCase):
    def test_success_with_request_and_response_payloads(self):
        client = Client(SubprocessMiddleware(LOGGER, wrapped_app))
        response = client.post(
            "/test_success_with_request_and_response_payloads",
            data=b"Non-UTF8 binary payload: \x80",
        )

        assert response.status == "200 OK"
        assert response.headers == Headers(
            [
                ("key1", "value1"),
                ("key2", "value2"),
            ]
        )
        assert [b for b in response.response] == [
            b"This is a ",
            b"non-UTF8 success response: \x80",
        ]

    def test_success_app_does_not_read_payload(self):
        client = Client(SubprocessMiddleware(LOGGER, wrapped_app))
        large_payload_data = bytearray(20 * 1024 * 1024)
        response = client.post(
            "/test_success_app_does_not_read_payload",
            data=bytes(large_payload_data),
        )

        assert response.status == "200 OK"
        assert [b for b in response.response] == [b"This is a successful response"]

    def test_success_with_payload_and_cpu_reservation_reset(self):
        reset_cpu_calls = []

        def reset_cpu_reservation_callback(num_cpus: int):
            reset_cpu_calls.append(num_cpus)

        client = Client(SubprocessMiddleware(LOGGER, wrapped_app))
        response = client.post(
            "/test_success_with_payload_and_cpu_reservation_reset",
            environ_overrides={"RESET_CPU_RESERVATION": reset_cpu_reservation_callback},
        )

        assert response.status == "200 OK"
        assert [b for b in response.response] == [b"This is a ", b"successful response"]
        assert reset_cpu_calls == [7]

    def test_no_cpu_reservation_reset_if_none_in_original_request(self):
        client = Client(SubprocessMiddleware(LOGGER, wrapped_app))
        response = client.post(
            "/test_no_cpu_reservation_reset_if_none_in_original_request",
        )

        assert response.status == "200 OK"
        assert [b for b in response.response] == [b"This is a successful response"]

    def test_failed_request_with_wsgi_error_output(self):
        client = Client(SubprocessMiddleware(LOGGER, wrapped_app))

        error_output = io.StringIO()
        response = client.post(
            "/test_failed_request_with_wsgi_error_output",
            environ_overrides={"wsgi.errors": error_output},
        )

        assert response.status == "500 Internal Server Error"
        assert [b for b in response.response] == []
        assert error_output.getvalue() == "First error output\nSecond error output\n"

    def test_exception_raised_in_wrapped_app(self):
        client = Client(SubprocessMiddleware(LOGGER, wrapped_app))

        with pytest.raises(Exception) as pytest_exc_info:
            client.post("/test_exception_raised_in_wrapped_app")

        exc_msg = pytest_exc_info.value.args[0]
        exc_traceback = "\n".join(traceback.format_tb(pytest_exc_info.tb))
        assert "This is an exception message" in exc_msg
        assert "test_subprocess_middleware.py" in exc_traceback
        assert "a_function_in_the_wrapped_app_callstack" in exc_traceback

    def test_exception_returned_from_start_response(self):
        client = Client(SubprocessMiddleware(LOGGER, wrapped_app))

        with pytest.raises(Exception) as pytest_exc_info:
            client.post("/test_exception_returned_from_start_response")

        exc_msg = pytest_exc_info.value.args[0]
        exc_traceback = "\n".join(traceback.format_tb(pytest_exc_info.tb))
        assert "This is an exception message" in exc_msg
        assert "test_subprocess_middleware.py" in exc_traceback
        assert "a_function_in_the_wrapped_app_callstack" in exc_traceback

    def test_wrapped_app_dies_from_signal(self):
        client = Client(SubprocessMiddleware(LOGGER, wrapped_app))

        with pytest.raises(Exception) as pytest_exc_info:
            client.post("/test_wrapped_app_dies_from_signal")

        exc_msg = pytest_exc_info.value.args[0]
        assert "Failed to read from WSGI request subprocess!" in exc_msg

    def test_globals_not_reinitialized_for_each_request(self):
        client = Client(SubprocessMiddleware(LOGGER, wrapped_app))

        response1 = client.post("/test_globals_not_reinitialized_for_each_request")
        response2 = client.post("/test_globals_not_reinitialized_for_each_request")

        response1_data = [b for b in response1.response]
        response2_data = [b for b in response2.response]

        assert response1_data[0].startswith(b"TEST_GLOBAL_VAR:")
        assert response1_data == response2_data

    def test_successful_subprocess_is_shut_down(self):
        exc = self.do_subprocess_shutdown_test(
            lambda middleware: Client(middleware).post(
                "/test_successful_subprocess_is_shut_down"
            )
        )
        assert exc is None

    def test_failing_subprocess_is_shut_down(self):
        exc = self.do_subprocess_shutdown_test(
            lambda middleware: Client(middleware).post(
                "/test_failing_subprocess_is_shut_down"
            )
        )
        assert exc is not None
        assert "This is an exception message" in exc.args[0]

    def test_client_disconnect_while_sending_request(self):
        def do_request(middleware: SubprocessMiddleware):
            # We do a manual WSGI call here, rather than using client.post(), so
            # that we can directly inject a LimitedStream into the middleware
            # that will throw a ClientDisconnected exception when reading from
            # it.
            # If we used client.post(), the exception would instead happen
            # outside of the middleware, which doesn't match what will happen in
            # real life if the client disconnects.
            environ = {
                "PATH_INFO": "/test_client_disconnect_while_sending_request",
                "CONTENT_LENGTH": 1,
                "wsgi.input": LimitedStream(io.BytesIO(), 1),
                "wsgi.errors": None,
            }

            def start_response(
                status: str,
                headers: Sequence[Tuple[str, str]],
                exc_info: Optional[ExcInfo],
            ) -> WriteCallable:
                assert False, "start_response callback should not have been called"

            for b in middleware(environ, start_response):
                pass

        exc = self.do_subprocess_shutdown_test(do_request)
        assert exc is not None
        assert "Client disconnected while writing request payload" in exc.args[0]

    @timeout_decorator.timeout(2)
    def do_subprocess_shutdown_test(
        self, request_func: Callable[[SubprocessMiddleware], None]
    ) -> Optional[Exception]:
        middleware = SubprocessMiddleware(LOGGER, wrapped_app)

        proc = Process(os.getpid())

        init_process = proc
        while init_process.pid != 1:
            init_process = init_process.parent()

        subprocesses_before = set(proc.children(recursive=True))
        init_subprocesses_before = set(init_process.children(recursive=True))

        try:
            request_func(middleware)
            return None
        except timeout_decorator.TimeoutError:
            raise
        except Exception as exc:
            return exc
        finally:
            subprocesses_after = set(proc.children(recursive=True))
            if subprocesses_before != subprocesses_after:
                # Avoid hanging the test itself in case it fails
                extra_processes = subprocesses_after.difference(subprocesses_before)
                for p in extra_processes:
                    p.terminate()

                assert False, f"Request subprocess didn't exit: {extra_processes}"

            # If the app leaked running subprocesses upon being killed, these will be orphaned by
            # the init process. To avoid getting false positives on this (in case the init process has
            # adopted some unrelated subprocesses while the test was being run), we only conclude that
            # a process was leaked if its cmdline matches a known string.
            init_subprocesses_after = set(init_process.children(recursive=True))
            if init_subprocesses_before != init_subprocesses_after:
                # Avoid hanging the test itself in case it fails
                extra_processes = init_subprocesses_after.difference(
                    init_subprocesses_before
                )
                leaked_subprocess = None
                for p in extra_processes:
                    if any(word for word in p.cmdline() if "HI FROM APP" in word):
                        leaked_subprocess = p
                        print(
                            f"Leaked subprocess: {leaked_subprocess} ({leaked_subprocess.cmdline()})"
                        )
                    p.terminate()

                if leaked_subprocess:
                    assert False, f"Subprocess was leaked: {leaked_subprocess}"
