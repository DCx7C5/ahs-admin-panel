import inspect
from dataclasses import dataclass
import logging
from uuid import UUID
from typing import (
    List,
    Dict,
    Callable, Coroutine, AsyncGenerator,
)

from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer

from backend.core.consumers.cmd_parser import CommandMapper

logger = logging.getLogger(__name__)


AHSUser = get_user_model()


@dataclass
class Command:
    """Dataclass representing a web socket message."""

    __slots__ = ('func_name', 'func_args', 'func_kwargs',
                 'owner', 'channel_name', 'page_name', 'app_name',
                 'send_resp_coro', 'unique_id', 'callback')
    func_name: str
    func_args: List[str | int | float | bool | UUID]
    func_kwargs: Dict[str, str | int | float | bool | UUID]
    owner: AHSUser
    channel_name: str
    page_name: str
    app_name: str
    unique_id: UUID | int
    callback: Callable[..., Coroutine] | AsyncGenerator | None

    def __post_init__(self):
        if not self.func_args:
            self.func_args = []
        if not self.func_kwargs:
            self.func_kwargs = {}
        if not self.callback:
            self.callback = CommandMapper.callbacks[self.func_name]['func']
        logger.debug(f"Created command: {self}")

    async def execute(self):
        logger.debug(f"Executing command: {self}")
        if self.validate_params():
            await self.send_response()


    async def send_response(self):
        channel_layer = get_channel_layer()
        ch_name = self.channel_name

        if inspect.isasyncgenfunction(self.callback):
            logger.debug(f"Sending async generator response for command: {self}, sending to {ch_name}")
            async for data in self.callback(*self.func_args, self.owner, **self.func_kwargs):
                await channel_layer.send(
                    ch_name,
                    {
                        'type': 'command.response',
                        'app': self.app_name,
                        'cmd': self.func_name,
                        'data': data,
                    }
                )
        else:
            logger.debug(f"Sending response for command: {self}")
            data = await self.callback(*self.func_args, self.owner ,**self.func_kwargs)
            await channel_layer.send(ch_name, {
                'type': 'command.response',
                'app': self.app_name,
                'cmd': self.func_name,
                'data': data,
            })


    def validate_params(self) -> bool:
        """Validates if the required parameters are included in the inputs."""
        return True


    def __repr__(self):
        return f"<Command func_name={self.func_name} func_args={self.func_args} func_kwargs={self.func_kwargs} owner={self.owner} channel_name={self.channel_name} >"
