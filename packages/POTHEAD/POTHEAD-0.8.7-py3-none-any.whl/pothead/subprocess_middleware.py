"""
WSGI middleware that spawns off a separate subprocess for each request.

Note: this is currently only suitable for use cases where the size of the
request payload is small, since it is read up-front instead of being streamed to
the inner WSGI app.
"""

import io
import multiprocessing
import psutil
from logging import Logger
from multiprocessing.connection import Connection
from tblib import pickling_support
from threading import Thread
import werkzeug

from typing import (
    cast,
    Any,
    Callable,
    Dict,
    Iterable,
    NamedTuple,
    Optional,
    Sequence,
    TextIO,
    Tuple,
)
from .wsgi_typing import (
    Environ,
    ExcInfo,
    StartResponse,
    WriteCallable,
    WsgiApplication,
)

# So that exception tracebacks can be moved across process boundaries
pickling_support.install()


class MsgStartResponse(NamedTuple):
    """
    Sent when the wrapped WSGI app has invoked the `start_response` callback.
    """

    http_status: str
    response_headers: Sequence[Tuple[str, str]]
    exc_info: Optional[ExcInfo]


class MsgData(NamedTuple):
    """
    Sent when the wrapped WSGI app generates payload bytes via `yield`.
    """

    data: bytes


class MsgWriteErrors(NamedTuple):
    """
    Sent when the wrapped WSGI app writes to "wsgi.errors" in its environment.
    """

    data: str


class MsgResetCpuReservation(NamedTuple):
    """
    Sent when the wrapped WSGI app invokes the RESET_CPU_RESERVATION callback
    (from the environment).
    """

    num_cpus: int


class MsgExceptionRaised(NamedTuple):
    """
    Sent if the wrapped WSGI app raises an exception while processing the request.
    """

    exc: BaseException


class MsgDone:
    """
    Sent when the wrapped WSGI app has finished processing the request without
    raising an exception. Note that this does not necessarily mean that the HTTP
    request itself was successful.
    """

    pass


def do_nothing_warmup():
    pass


class SubprocessMiddleware:
    def __init__(self, logger: Logger, wrapped_app: WsgiApplication):
        """
        wrapped_app: WsgiApplication
            The underlying WSGI app, which will have each of its requests called
            in a separate subprocess.
        """
        self.logger = logger
        self.wrapped_app = wrapped_app

        # Use a forkserver with the app's module preloaded, to make the
        # spawning of subprocesses for each request faster.
        self.forkserver_context = multiprocessing.get_context("forkserver")
        preload_module_names = [wrapped_app.__module__]
        self.forkserver_context.set_forkserver_preload(preload_module_names)

        # Spawning the very first subprocess instance is a lot slower than subsequent
        # spawns, so do that right away to make the actual requests fast.
        warmup_subprocess = self.forkserver_context.Process(target=do_nothing_warmup)
        warmup_subprocess.start()
        warmup_subprocess.join()

    def __call__(
        self, environ: Environ, start_response: StartResponse
    ) -> Iterable[bytes]:
        """
        Implementation of the WSGI app interface.
        """

        new_environ = {k: v for k, v in environ.items()}
        new_environ["wsgi.multiprocess"] = True
        new_environ["wsgi.multithread"] = False
        new_environ.pop("werkzeug.request", None)
        new_environ.pop("werkzeug.server.shutdown", None)

        # These two streams are replaced by pipe communication with the subprocess
        new_environ.pop("wsgi.input")
        wsgi_errors = cast(TextIO, new_environ.pop("wsgi.errors"))

        # RESET_CPU_RESERVATION is a callback function, which cannot be moved
        # across process boundaries. The provided callback (if any) is saved
        # here, and then invoked when the subprocess sends a specific message
        # over the pipe.
        reset_cpu_reservation = cast(
            Optional[Callable[[int], None]],
            new_environ.pop("RESET_CPU_RESERVATION", None),
        )

        # Set up the thread for reading the wsgi.input data
        (wsgi_input_reader, wsgi_input_writer) = self.forkserver_context.Pipe(
            duplex=False
        )
        request_sender_thread = Thread(
            target=SubprocessMiddleware.send_request_data,
            args=(self.logger, environ, wsgi_input_writer),
        )

        # Setup up the subprocess for running the wrapped WSGI app
        (msg_reader, msg_writer) = self.forkserver_context.Pipe(duplex=False)
        subprocess = self.forkserver_context.Process(
            target=subprocess_main,
            name="WSGI request subprocess",
            args=(
                self.wrapped_app,
                new_environ,
                msg_writer,
                wsgi_input_reader,
                reset_cpu_reservation is not None,
            ),
        )
        try:
            request_sender_thread.start()
            subprocess.start()

            # Close our instances of the unused sides of the connections, so that
            # once the subprocess closes its instance, the connection will be
            # completely closed and recv() and similar methods will indicate EOF.
            msg_writer.close()
            wsgi_input_reader.close()

            while True:
                try:
                    msg = msg_reader.recv()
                except EOFError:
                    # This should not normally happen even if the wrapped app raises
                    # an exception during processing, and likely indicates that the
                    # subprocess died from receiving a signal.
                    raise Exception("Failed to read from WSGI request subprocess!")

                if isinstance(msg, MsgStartResponse):
                    start_response(msg.http_status, msg.response_headers, msg.exc_info)
                elif isinstance(msg, MsgData):
                    yield msg.data
                elif isinstance(msg, MsgWriteErrors):
                    wsgi_errors.write(msg.data)
                elif isinstance(msg, MsgResetCpuReservation):
                    if reset_cpu_reservation is not None:
                        reset_cpu_reservation(msg.num_cpus)
                elif isinstance(msg, MsgExceptionRaised):
                    raise msg.exc
                elif isinstance(msg, MsgDone):
                    break
                else:
                    assert (
                        False
                    ), f"Got unknown message type from WSGI subprocess: {msg}"
        finally:
            _kill_process_and_its_descendants(subprocess)
            request_sender_thread.join()

    @staticmethod
    def send_request_data(logger: Logger, environ: Environ, writer: Connection):
        try:
            with writer:
                request_data = werkzeug.Request(
                    cast(Dict[str, Any], environ)
                ).stream.read()
                writer.send_bytes(request_data)
        except werkzeug.exceptions.ClientDisconnected:
            # Since we have closed the writer at this point, the subprocess will
            # fail to read from the other side, and that exception will be
            # transported to the main process. So we can just log here, and then
            # let the thread finish.
            logger.warning("Request reader thread exited due to client disconnect")


# Sends data written by the wrapped app to wsgi.errors back to
# the main process via a pipe.
class WSGIErrors:
    def __init__(self, writer: Connection):
        self.writer = writer

    def write(self, data: str):
        self.writer.send(MsgWriteErrors(data))


def subprocess_main(
    wrapped_app: WsgiApplication,
    environ: Environ,
    msg_writer: Connection,
    wsgi_input_reader: Connection,
    has_reset_cpu_reservation_callback,
):
    with msg_writer, wsgi_input_reader:
        try:

            def wrapped_start_response(
                http_status: str,
                headers: Sequence[Tuple[str, str]],
                exc_info: Optional[ExcInfo] = None,
            ) -> WriteCallable:
                """Implements the "start response callback" WSGI interface"""

                msg_writer.send(MsgStartResponse(http_status, headers, exc_info))

                def disabled_write_callback(data: bytes) -> Any:
                    raise Exception(
                        "Write callback not supported with SubprocessMiddleware: "
                        + "Use `yield` to generate payload data instead."
                    )

                return disabled_write_callback

            def reset_cpu_reservation(num_cpus: int):
                msg_writer.send(MsgResetCpuReservation(num_cpus))

            new_environ = {k: v for k, v in environ.items()}

            # Set up the CPU reservation callback if the original request had one
            assert "RESET_CPU_RESERVATION" not in environ
            if has_reset_cpu_reservation_callback:
                new_environ["RESET_CPU_RESERVATION"] = reset_cpu_reservation

            # Read the request data from the parent process
            try:
                request_data = wsgi_input_reader.recv_bytes()
            except EOFError:
                raise Exception("Client disconnected while writing request payload")

            assert isinstance(request_data, bytes)
            new_environ["wsgi.input"] = io.BytesIO(request_data)

            # Set up a proxy output stream for WSGI errors that send them
            # back to the parent process.
            new_environ["wsgi.errors"] = WSGIErrors(msg_writer)

            # Make the actual WSGI call to the wrapped app
            for output_data in wrapped_app(new_environ, wrapped_start_response):
                msg_writer.send(MsgData(output_data))

            msg_writer.send(MsgDone())
        except Exception as exc:
            msg_writer.send(MsgExceptionRaised(exc))
            raise


def _suspend_recursive(pid: psutil.Process) -> Iterable[psutil.Process]:
    """Gets a list of process and descendants. The only way to do it ~"atomically", is to suspend
    them in the process, preventing them from forking or dying while we're looking the other way.

    Returns a list of now suspended processes, including the root specified by pid"""
    try:
        proc = psutil.Process(pid)
        proc.suspend()
    except psutil.NoSuchProcess:
        return []

    descendants = {proc}
    while True:
        prior_count = len(descendants)
        try:
            for child in proc.children(recursive=True):
                if child not in descendants:
                    child.suspend()
                descendants.add(child)
        except psutil.NoSuchProcess:
            if proc.is_running():
                continue
            else:
                return []
        if len(descendants) == prior_count:
            break

    return descendants


def _kill_process_and_its_descendants(process: multiprocessing.Process):
    descendants = _suspend_recursive(process.pid)

    for descendant in descendants:
        try:
            descendant.kill()
        except psutil.NoSuchProcess:
            # Without a defined order, descendants might be already orphaned, adopted and killed
            # by init when we get to them
            continue

    process.join()
