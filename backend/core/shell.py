import asyncio
import collections
import logging
import os
import pty
import signal
import stat
import warnings
from asyncio import (
    ReadTransport,
    WriteTransport,
    BaseProtocol,
    Protocol,
    Transport,
    StreamReader,
    StreamWriter,
    BaseTransport,
    AbstractEventLoop,
)

logger = logging.getLogger(__name__)

def add_fd_reader(fd, callback, *args):
    loop = asyncio.get_event_loop()
    loop.add_reader(fd, callback, *args)
    
def add_fd_writer(fd, callback, *args):
    loop = asyncio.get_event_loop()
    loop.add_writer(fd, callback, *args)

def remove_fd_reader(fd):
    loop = asyncio.get_event_loop()
    loop.remove_reader(fd)

def remove_fd_writer(fd):
    loop = asyncio.get_event_loop()
    loop.remove_writer(fd)


class FileDescriptorError(Exception):
    def __init__(self, fd, message):
        super().__init__(message)
        self.message = f"Error on FD {fd}: {message}"
        self.fd = fd
        logger.error(self.message)


class ProtocolError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        logger.error(self.message)

    async def connect_write_pipe(self, protocol_factory, pipe):
        protocol = protocol_factory()
        waiter = self.create_future()
        transport = self._make_write_pipe_transport(pipe, protocol, waiter)

        try:
            await waiter
        except:
            transport.close()
            raise

        if self._debug:
            logger.debug('Write pipe %r connected: (%r, %r)',
                         pipe.fileno(), transport, protocol)
        return transport, protocol


class ReadFileDescriptorTransport(ReadTransport):
    max_size = 256 * 1024  # Maximum bytes to read in a single event loop iteration

    def __init__(self, fd: int, protocol: Protocol, waiter=None, extra=None, loop: asyncio.AbstractEventLoop = None):
        super().__init__(extra)
        self._extra = extra if extra else {}
        self._extra["fd"] = fd

        self._loop = loop if loop else asyncio.get_event_loop()
        self._fd = fd
        self._protocol = protocol
        self._closing = False
        self._paused = False

        # Check if the FD is valid
        mode = os.fstat(self._fd).st_mode
        if not stat.S_ISCHR(mode):
            raise FileDescriptorError(
                self._fd, "FD transport is only for readable file descriptors."
            )

        os.set_blocking(self._fd, False)  # Set to non-blocking mode

        # Notify the protocol of the connection
        self._loop.call_soon(self._protocol.connection_made, self)

        # Schedule the FD to be read when data is available
        self._loop.call_soon(self._add_reader, self._fd, self._read_ready)
        if waiter is not None:
            self._loop.call_soon(asyncio.Future.set_result, waiter,)

    def _add_reader(self, fd, callback):
        if not self.is_reading():
            return
        add_fd_reader(fd, callback)

    def is_reading(self):
        return not self._paused and not self._closing

    def _read_ready(self):
        try:
            data = os.read(self._fd, self.max_size)
        except (BlockingIOError, InterruptedError):
            pass
        except OSError as exc:
            self._fatal_error(exc, "Fatal read error on FD transport")
        else:
            if data:
                self._protocol.data_received(data)
            else:
                # EOF case
                self._closing = True
                self._loop.remove_reader(self._fd)
                # self._loop.call_soon(self._protocol.eof_received, )
                self._loop.call_soon(self._call_connection_lost, None)

    def pause_reading(self):
        if not self.is_reading():
            return
        self._paused = True
        self._loop.remove_reader(self._fd)

    def resume_reading(self):
        if self._closing or not self._paused:
            return
        self._paused = False
        add_fd_reader(self._fd, self._read_ready, (0,))

    def close(self):
        if not self._closing:
            self._close(None)

    def _fatal_error(self, exc, message="Fatal error on FD transport"):
        self._loop.call_exception_handler(
            {"message": message, "exception": exc, "transport": self, "protocol": self._protocol}
        )
        self._close(exc)

    def _close(self, exc):
        self._closing = True
        self._loop.remove_reader(self._fd)
        self._loop.call_soon(self._call_connection_lost, exc)

    def _call_connection_lost(self, exc):
        try:
            self._protocol.connection_lost(exc)
        finally:
            try:
                os.close(self._fd)
            except OSError as exc:
                logger.error(f"Error closing FD {self._fd}: {exc}")
            self._fd = None
            self._protocol = None
            self._loop = None

    def is_closing(self):
        return self._closing


class WriteFileDescriptorTransport(WriteTransport):
    def __init__(self, fd: int, protocol: BaseProtocol, waiter=None, extra=None, loop: asyncio.AbstractEventLoop = None,):
        super().__init__(extra)
        self._loop = loop if loop else asyncio.get_event_loop()
        self._fd = fd
        self._protocol = protocol
        self._closing = False
        self._buffer = bytearray()

        # Check if the FD is valid for writing
        mode = os.fstat(fd).st_mode
        if not (stat.S_ISREG(mode) or stat.S_ISCHR(mode) or stat.S_ISBLK(mode) or stat.S_ISSOCK(mode)):
            raise FileDescriptorError(fd, f"FD {fd} is not valid for writing.")

        os.set_blocking(fd, False)  # Set to non-blocking

        # Notify the protocol of the connection
        self._loop.call_soon(self._protocol.connection_made, self)
        if waiter is not None:
            self._loop.call_soon(asyncio.Future.set_result, waiter,)

    def write(self, data: bytes):
        if self._closing:
            raise RuntimeError("Cannot write to closing transport")
        if not isinstance(data, (bytes, memoryview, bytearray)):
            raise TypeError(f"Data must be bytes-like, not {type(data).__name__}.")
        if not data:
            return
        self._buffer.extend(data)
        add_fd_writer(self._fd, self._write_ready)

    def _write_ready(self):
        try:
            written = os.write(self._fd, self._buffer)
            del self._buffer[:written]
        except (BlockingIOError, InterruptedError):
            pass
        except OSError as exc:
            self._fatal_error(exc, "Fatal write error on FD transport")
        finally:
            if not self._buffer:
                self._loop.remove_writer(self._fd)
            if self._closing and not self._buffer:
                self._close(None)

    def close(self):
        if not self._closing:
            self._closing = True
            if not self._buffer:
                self._close(None)

    def _fatal_error(self, exc, message="Fatal write error on FD transport"):
        self._loop.call_exception_handler(
            {"message": message, "exception": exc, "transport": self, "protocol": self._protocol}
        )
        self._close(exc)

    def _close(self, exc):
        self._closing = True
        self._loop.remove_writer(self._fd)
        self._loop.call_soon(self._call_connection_lost, exc)

    def _call_connection_lost(self, exc):
        try:
            self._protocol.connection_lost(exc)
        finally:
            try:
                os.close(self._fd)
            except OSError as exc:
                logger.error(f"Error closing FD {self._fd}: {exc}")
            self._fd = None
            self._protocol = None
            self._loop = None


class PTYTransport(BaseTransport):

    __slots__ = ()

    def get_pid(self):
        """Get subprocess id."""
        raise NotImplementedError

    def get_returncode(self):
        raise NotImplementedError

    def get_fd_transport(self, fd):
        """Get transport with number fd."""
        raise NotImplementedError

    def send_signal(self, signal):
        raise NotImplementedError

    def terminate(self):
        raise NotImplementedError

    def kill(self):
        raise NotImplementedError


class WritePtyConsumerProto(BaseProtocol):

    def __init__(self, fd, loop: asyncio.AbstractEventLoop = None):
        self._loop = loop if loop else asyncio.get_event_loop()
        self.proc = AHSPTYTransport()
        self.fd = fd
        self.consumer = None
        self.disconnected = False

    def connection_made(self, transport):
        self.consumer = transport

    def __repr__(self):
        return f'<{self.__class__.__name__} fd={self.fd} consumers={self.consumer!r}>'

    def connection_lost(self, exc):
        self.disconnected = True
        self.proc._consumer_connection_lost(self.fd, exc)
        self.proc = None

    def pause_writing(self):
        self.proc._protocol.pause_writing()

    def resume_writing(self):
        self.proc._protocol.resume_writing()


class ReadPtyConsumerProto(WritePtyConsumerProto, Protocol):

    def data_received(self, data):
        self.proc._consumer_data_received(self.fd, data)


class PtyShellProcess:
    __slots__ = ('proc', 'pid', 'master_fd', 'slave_fd', '_read_task', '_loop',
                 'reader', 'writer', '_consumer_send_coro', '_writer', '_read_transport', '_write_transport')

    def __init__(self, loop: AbstractEventLoop = None):
        self._loop: AbstractEventLoop = loop if loop else asyncio.get_event_loop()
        self.master_fd: int | None = None
        self.pid: int | None = None
        self.reader: StreamReader | None = None
        self.writer: StreamWriter | None = None
        self._read_transport: ReadFileDescriptorTransport | None = None
        self._write_transport: WriteFileDescriptorTransport | None = None
        self.get_pty() # creates pty

    def get_pty(self):
        master_fd, slave_fd = pty.openpty()
        pid, m = pty.fork()
        if pid == 0:
            # Child process
            os.close(master_fd)  # Close the master FD in the child

            # Redirect stdin, stdout, and stderr to the PTY slave
            os.dup2(slave_fd, 0)
            os.dup2(slave_fd, 1)
            os.dup2(slave_fd, 2)
            os.close(slave_fd)

            # Execute a command
            # os.execvp("sh", ["sh", "-c", f"echo shit-{os.getpid()}-{os.getppid()} | nc localhost 8888"])
            os.execvp('/bin/bash', ['/bin/bash'])
        else:
            os.close(slave_fd)
            self.master_fd, self.pid = master_fd, pid

    def __repr__(self):
        return f"<ShellProcess pid={self.pid} master_fd={self.master_fd} >"

    def kill(self):
        """Immediately kill the child process."""
        if self.pid:
            try:
                os.kill(self.pid, signal.SIGKILL)  # Send SIGKILL to terminate the process
                logger.info(f"Shell process {self.pid} killed successfully.")
            except ProcessLookupError:
                logger.warning(f"Process {self.pid} does not exist.")
            except Exception as e:
                logger.error(f"Failed to kill process {self.pid}: {e}")
        else:
            logger.error("No process to kill.")

    def terminate(self):
        """Gracefully terminate the child process."""
        if self.pid:
            try:
                os.kill(self.pid, signal.SIGTERM)  # Send SIGTERM to allow graceful termination
                logger.info(f"Shell process {self.pid} terminated successfully.")
            except ProcessLookupError:
                logger.warning(f"Process {self.pid} does not exist.")
            except Exception as e:
                logger.error(f"Failed to terminate process {self.pid}: {e}")
        else:
            logger.error("No process to terminate.")

    def cleanup(self):
        """Clean up resources (close file descriptors and reap child process)."""
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except OSError as e:
                logger.error(f"Failed to close master_fd {self.master_fd}: {e}")
            logger.info(f"Closed master_fd {self.master_fd}.")

        if self.pid:
            try:
                os.waitpid(self.pid, 0)  # Reap the child process
                logger.info(f"Reaped process {self.pid}.")
            except ChildProcessError:
                logger.warning(f"No child process found with pid {self.pid}.")
            except Exception as e:
                logger.error(f"Error while reaping process {self.pid}: {e}")


class AHSPTYTransport(PTYTransport):

    def __init__(self, protocol, args, waiter=None, extra=None, loop: AbstractEventLoop = None ,**kwargs):
        super().__init__(extra)
        self._closed = False
        self._protocol = protocol
        self._loop = loop if loop else asyncio.get_event_loop()
        self._proc: PtyShellProcess | None = None
        self._pid = None
        self._returncode = None
        self._exit_waiters = []
        self._pending_calls = collections.deque()
        self._pipes = {}
        self._finished = False

        # Create the child process: set the _proc attribute
        try:
            self._proc = PtyShellProcess(self._loop)
        except:
            self.close()
            raise

        self._extra = {'subprocess': self._proc}

        if self._loop.get_debug():
            if isinstance(args, (bytes, str)):
                program = args
            else:
                program = args[0]
            logger.debug('process %r created: pid %s',
                         program, self._pid)

        self._loop.create_task(self._connect_pipes(waiter))

    def __repr__(self):
        info = [self.__class__.__name__]
        if self._closed:
            info.append('closed')
        if self._pid is not None:
            info.append(f'pid={self._pid}')
        if self._returncode is not None:
            info.append(f'returncode={self._returncode}')
        elif self._pid is not None:
            info.append('running')
        else:
            info.append('not started')

        stdin = self._pipes.get(0)
        if stdin is not None:
            info.append(f'stdin={stdin.pipe}')

        stdout = self._pipes.get(1)
        stderr = self._pipes.get(2)
        if stdout is not None and stderr is stdout:
            info.append(f'stdout=stderr={stdout.pipe}')
        else:
            if stdout is not None:
                info.append(f'stdout={stdout.pipe}')
            if stderr is not None:
                info.append(f'stderr={stderr.pipe}')

        return '<{}>'.format(' '.join(info))

    def set_protocol(self, protocol):
        self._protocol = protocol

    def get_protocol(self):
        return self._protocol

    def is_closing(self):
        return self._closed

    def close(self):
        if self._closed:
            return
        self._closed = True

        for proto in self._pipes.values():
            if proto is None:
                continue
            proto.pipe.close()

        if (self._proc is not None and
                # has the child process finished?
                self._returncode is None and
                # the child process has finished, but the
                # transport hasn't been notified yet?
                self._proc.poll() is None):

            if self._loop.get_debug():
                logger.warning('Close running child process: kill %r', self)

            try:
                self._proc.kill()
            except ProcessLookupError:
                pass

            # Don't clear the _proc reference yet: _post_init() may still run

    def __del__(self, _warn=warnings.warn):
        if not self._closed:
            _warn(f"unclosed transport {self!r}", ResourceWarning, source=self)
            self.close()

    def get_pid(self):
        return self._pid

    def get_returncode(self):
        return self._returncode

    def get_pipe_transport(self, fd):
        if fd in self._pipes:
            return self._pipes[fd].pipe
        else:
            return None

    def _check_proc(self):
        if self._proc is None:
            raise ProcessLookupError()

    def send_signal(self, signal):
        self._check_proc()
        self._proc.send_signal(signal)

    def terminate(self):
        self._check_proc()
        self._proc.terminate()

    def kill(self):
        self._check_proc()
        self._proc.kill()

    async def _connect_pipes(self, waiter):
        try:
            proc = self._proc
            loop = self._loop

            if proc.stdin is not None:
                _, pipe = await loop.connect_write_pipe(
                    lambda: WritePtyConsumerProto(self, self._proc),
                    proc.stdin)
                self._pipes[0] = pipe

            if proc.stdout is not None:
                _, pipe = await loop.connect_read_pipe(
                    lambda: ReadPtyConsumerProto(self, self._proc),
                    proc.stderr)
                self._pipes[2] = pipe


            loop.call_soon(self._protocol.connection_made, self)
            for callback, data in self._pending_calls:
                loop.call_soon(callback, *data)
            self._pending_calls = None
        except (SystemExit, KeyboardInterrupt):
            raise
        except BaseException as exc:
            if waiter is not None and not waiter.cancelled():
                waiter.set_exception(exc)
        else:
            if waiter is not None and not waiter.cancelled():
                waiter.set_result(None)

    def _call(self, cb, *data):
        if self._pending_calls is not None:
            self._pending_calls.append((cb, data))
        else:
            self._loop.call_soon(cb, *data)

    def _consumer_connection_lost(self, fd, exc):
        self._call(self._protocol.pipe_connection_lost, fd, exc)
        self._try_finish()

    def _consumer_data_received(self, fd, data):
        self._call(self._protocol.pipe_data_received, fd, data)

    def _process_exited(self, returncode):
        if self._loop.get_debug():
            logger.info('%r exited with return code %r', self, returncode)
        self._returncode = returncode
        if self._proc.returncode is None:
            # asyncio uses a child watcher: copy the status into the Popen
            # object. On Python 3.6, it is required to avoid a ResourceWarning.
            self._proc.returncode = returncode
        self._call(self._protocol.process_exited)

        self._try_finish()

    async def _wait(self):
        """Wait until the process exit and return the process return code.

        This method is a coroutine."""
        if self._returncode is not None:
            return self._returncode

        waiter = self._loop.create_future()
        self._exit_waiters.append(waiter)
        return await waiter

    def _try_finish(self):
        if self._returncode is None:
            return
        if all(p is not None and p.disconnected
               for p in self._pipes.values()):
            self._finished = True
            self._call(self._call_connection_lost, None)

    def _call_connection_lost(self, exc):
        try:
            self._protocol.connection_lost(exc)
        finally:
            # wake up futures waiting for wait()
            for waiter in self._exit_waiters:
                if not waiter.cancelled():
                    waiter.set_result(self._returncode)
            self._exit_waiters = None
            self._loop = None
            self._proc = None
            self._protocol = None


class ReadFDProtocol(Protocol):

    def __init__(self, fd, consumer_send_func: callable = None):
        self.fd = fd
        self._loop = asyncio.get_event_loop()
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        logger.debug(f"ReadFDProtocol connection_made transport: {transport}")



class WriteFDProtocol(Protocol):
    def __init__(self, fd, consumer_send_func: callable = None):
        self.fd = fd
        self.consumer_send_func = consumer_send_func
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport



class ReadConsumerTransport(ReadTransport):

    def __init__(self, fd: int, protocol: Protocol, waiter=None, extra=None, loop: asyncio.AbstractEventLoop = None):
        super().__init__(extra)
        self._extra = extra if extra else {}
        self._extra["fd"] = fd
        self._loop = loop if loop else asyncio.get_event_loop()
        self._fd = fd
        self._protocol = protocol
        self._closing = False
        self._paused = False

        # Notify the protocol of the connection
        self._loop.call_soon(self._protocol.connection_made, self)



class WriteConsumerTransport(WriteTransport):

    def __init__(self, fd: int, protocol: BaseProtocol, waiter=None, extra=None, loop: asyncio.AbstractEventLoop = None,):
        super().__init__(extra)
        self._loop = loop if loop else asyncio.get_event_loop()
        self._fd = fd
        self._protocol = protocol
        self._closing = False
        self._buffer = bytearray()

        # Check if the FD is valid for writing
        mode = os.fstat(fd).st_mode
        if not stat.S_ISCHR(mode):
            raise FileDescriptorError(fd, f"FD {fd} is not valid for writing.")

        os.set_blocking(fd, False)  # Set to non-blocking

        # Notify the protocol of the connection
        self._loop.call_soon(self._protocol.connection_made, self)



class WriteConsumerProtocol(Protocol):
    """"""

    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        """Called when a connection is made."""
        self.transport = transport
        logger.debug(f"WriteConsumerProtocol connection_made transport: {transport}")

    def data_received(self, data):
        """Data received from the PTY."""
        logger.debug(f"WriteConsumerProtocol data_received data: {data}")

    def eof_received(self):
        logger.warning(f"WriteConsumerProtocol eof_received")

    def connection_lost(self, exc):
        logger.error(f"WriteConsumerProtocol connection_lost exc: {exc}")


class ReadConsumerProtocol(BaseProtocol):

    def __init__(self):
        self.transport = None
        self.pty_read_transport = None

    def connection_made(self, transport):
        """Called when a connection is made."""
        self.transport = transport
        logger.debug(f"ReadConsumerProtocol connection_made transport: {transport}")

    def data_received(self, data):
        """Data received from the Django Websocket"""
        self.transport.write(data)
        logger.debug(f"ReadConsumerProtocol data_received data: {data}")

    def connection_lost(self, exc):
        logger.error(f"ReadConsumerProtocol connection_lost exc: {exc}")

    def eof_received(self):
        logger.warning(f"ReadConsumerProtocol eof_received")


transport = Transport

class TerminalProtocol(Protocol):
    __slots__ = () # is basically AsyncWebSocketConsumer

    def __init__(self):
        self._loop = asyncio.get_event_loop()
        self._limit = 2**8
        self.transport = None
        self.stdin = None
        self.stdout = None


    def connection_made(self, transport):
        """Called when a connection is made."""
        self.transport = transport
        logger.debug(f"PtyFdConsumerProtocol connection_made transport: {transport}")

        stdout_transport = ReadFileDescriptorTransport(1, self, loop=self._loop)
        self.stdout = StreamReader(limit=self._limit, loop=self._loop)
        self.stdout.set_transport(stdout_transport)


        stdin_transport = WriteFileDescriptorTransport(0, self, loop=self._loop)
        if stdin_transport is not None:
            self.stdin = StreamWriter(stdin_transport,
                                              protocol=self,
                                              reader=None,
                                              loop=self._loop)

    def data_received(self, data):
        """Data received from the PTY."""
        logger.debug(f"PtyFdConsumerProtocol data_received data: {data}")

    def eof_received(self):
        logger.warning(f"PtyFdConsumerProtocol eof_received")

    def connection_lost(self, exc):
        logger.error(f"PtyFdConsumerProtocol connection_lost exc: {exc}")

    def send_data(self, data: bytes):
        self.transport.write(data)

    def close(self):
        logger.info(f"PtyFdConsumerProtocol close")
        self.transport.close()


class PTYProtocol(Protocol):


    def __init__(self, on_data_callback):
        self.on_data_callback = on_data_callback
        self.transport = None
        self.buffer = b""

    def connection_made(self, transport):
        """
        Called when PTY transport is established.
        """
        self.transport = transport
        logger.info("[PTY] Connection established.")

    def data_received(self, data):
        """
        Called when data is read from the PTY.
        Sends the data to the WebSocket consumers via the callback.
        """
        if self.on_data_callback:
            asyncio.create_task(self.on_data_callback(data))

    def write_to_pty(self, data):
        if hasattr(self.transport, "write"):
            self.transport.write(data)
        else:
            # Log or handle this gracefully
            raise RuntimeError(f"Transport does not support write: {self.transport}")

    def connection_lost(self, exc):
        """
        Called when the PTY connection is lost.
        """
        if exc:
            logger.error(f"[PTY] Connection lost with error: {exc}")
        else:
            logger.info("[PTY] Connection closed.")
        self.transport = None

    def close(self):
        """
        Close the PTY transport.
        """
        if self.transport:
            self.transport.close()
            print("[PTY] Transport closed.")
