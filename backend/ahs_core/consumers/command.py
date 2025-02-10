import inspect
import json
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

from backend.ahs_core.consumers.cmd_parser import CommandMapper

logger = logging.getLogger(__name__)


User = get_user_model()


@dataclass
class Command:
    """Dataclass representing a web socket message."""

    __slots__ = ('func_name', 'func_args', 'func_kwargs',
                 'owner', 'channel_name', 'page_name', 'app_name',
                 'send_resp_coro', 'unique_id', 'callback', 'socket_url',)
    func_name: str
    func_args: List[str | int | float | bool | UUID]
    func_kwargs: Dict[str, str | int | float | bool | UUID]
    owner: User
    channel_name: str
    page_name: str
    app_name: str
    unique_id: UUID | int
    socket_url: str
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
                        'channel_name': ch_name,
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
                'channel_name': ch_name,
                'data': data,
            })

    def validate_params(self):
        sig = inspect.signature(self.callback)
        bound_args = sig.bind(*self.func_args, **self.func_kwargs)
        bound_args.apply_defaults()
        return True

    def json_serialize(self):
        return json.dumps({
            'func_name': self.func_name,
            'func_args': self.func_args,
            'func_kwargs': self.func_kwargs,
            'owner': self.owner.id,
            'channel_name': self.channel_name,
            'page_name': self.page_name,
            'app_name': self.app_name,
            'unique_id': self.unique_id,
            'callback': self.callback.__name__,
            'socket_url': self.socket_url,
        })

    def from_command(self):
        return self.json_serialize()

    def json_deserialize(self, json_str):
        data = json.loads(json_str)
        return Command(
            func_name=data['func_name'],
            func_args=data['func_args'],
            func_kwargs=data['func_kwargs'],
            owner=User.objects.get(id=data['owner']),
            channel_name=data['channel_name'],
            page_name=data['page_name'],
            app_name=data['app_name'],
            unique_id=data['unique_id'],
            callback=CommandMapper.callbacks[data['func_name']]['func'],
            socket_url=f"{self.socket_url}?id={data['unique_id']}",
        )

    def __repr__(self):
        return f"<Command func_name={self.func_name} func_args={self.func_args} func_kwargs={self.func_kwargs} owner={self.owner} channel_name={self.channel_name} >"

    def __hash__(self):
        return hash(self.json_serialize())
