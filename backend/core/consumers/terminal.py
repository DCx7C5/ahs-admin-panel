import asyncio
import json
import os
import pty
import signal
import struct
import fcntl
import termios

import logging
from typing import TypeVar, Mapping
from channels.generic.websocket import AsyncWebsocketConsumer
from channels_redis.core import RedisChannelLayer

logger = logging.getLogger(__name__)

RCL = TypeVar('RCL', bound=RedisChannelLayer)
MsgVar = Mapping


LIMIT = 2**8


def set_winsize(fd, col, row):
    s = struct.pack("HHHH", row, col, 0, 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, s)  #



class AsyncWebsocketTerminal(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pty_master = None
        self.pty_slave = None
        self.process_pid = None

    async def connect(self):
        """
        Called when the WebSocket connection is established.
        Set up the PTY and start the subprocess (command/shell).
        """
        await self.accept()
        logger.info(f"WebSocket connection accepted: {self.scope['client']}")
        # Create a pseudo-Terminal
        self.pty_master, self.pty_slave = pty.openpty()

        # Fork a new process
        self.process_pid = os.fork()
        if self.process_pid == 0:  # In child process
            os.setsid()  # Create a new session ID for the new process
            os.dup2(self.pty_slave, 0)  # Redirect stdin
            os.dup2(self.pty_slave, 1)  # Redirect stdout
            os.dup2(self.pty_slave, 2)  # Redirect stderr
            os.close(self.pty_slave)
            os.close(self.pty_master)
            os.execvp("/bin/zsh", ["/bin/zsh"])  # noqa Replace child process with shell

        else:  # In parent process
            # Close the slave side in the parent process
            os.close(self.pty_slave)

            # Add a reader to monitor PTY's master for output
            loop = asyncio.get_event_loop()
            loop.add_reader(self.pty_master, self.pty_output_reader)


    async def disconnect(self, close_code):
        """
        Called when the WebSocket is disconnected.
        Cleans up resources like PTY and subprocess.
        """
        if self.process_pid:
            try:
                # Send SIGTERM for graceful shutdown
                os.killpg(os.getpgid(self.process_pid), signal.SIGTERM)
                for _ in range(5):  # Wait up to 5 seconds for termination
                    _, status = os.waitpid(self.process_pid, os.WNOHANG)
                    if status != 0:  # Process terminated
                        logger.info(f"Process group {os.getpgid(self.process_pid)} terminated gracefully.")
                        break
                    await asyncio.sleep(1)
                else:
                    # Force kill on timeout
                    os.killpg(os.getpgid(self.process_pid), signal.SIGKILL)
                    _, status = os.waitpid(self.process_pid, 0)
                    logger.info(f"Process group {os.getpgid(self.process_pid)} killed forcefully.")
            except ProcessLookupError:
                logger.warning("Process group already terminated.")

        # Remove reader and clean up PTY master
        loop = asyncio.get_event_loop()
        if self.pty_master:
            loop.remove_reader(self.pty_master)

            try:
                # Close the master file descriptor (release resources)
                os.close(self.pty_master)
                self.pty_master = None
                logger.info("PTY master file descriptor closed successfully.")
            except OSError as e:
                logger.error(f"Error closing PTY master descriptor: {e}")

    async def websocket_receive(self, data, **kwargs):
        """
        Called when WebSocket receives data.
        Write data to the PTY (subprocess's stdin).
        """
        # if resize
        logger.debug(f"websocket_receive: {data}")
        if isinstance(data, dict) and 'bytes' in data:
            data = data['bytes']
            os.write(self.pty_master, data)

        else:
            data = data.get('text', '')
            if len(data) < 1:
                return
            elif len(data) == 1:
                os.write(self.pty_master, data.encode('utf-8'))
            elif data.startswith('{') and data.endswith('}'):
                logger.debug(f"resize: {json.loads(data)}")
                data = json.loads(data)
                set_winsize(
                    self.pty_master,
                    data['cols'],
                    data['rows']
                )
            else:
                os.write(self.pty_master, data.encode('utf-8'))

    def pty_output_reader(self):
        """
        Called when the PTY master has data to read.
        Reads stdout/stderr output and sends it to WebSocket.
        """
        try:
            output = os.read(self.pty_master, 1024)
            asyncio.create_task(self.send(bytes_data=output))  # Send data to WebSocket
        except OSError:
            # Handle case where the process exits, and PTY is closed
            pass
