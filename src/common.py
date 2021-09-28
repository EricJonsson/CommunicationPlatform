# coding: utf-8

import json
from functools import wraps
from typing import Dict, Callable, Optional

from socketio import Server, Client


def unpack(
        event: str,
        dict_handler: Callable[[str, Dict], None],
        logger=None,
        data_arg_pos=1
) -> Callable[[str, str], None]:
    @wraps(dict_handler)
    def _handler(*args):
        if data_arg_pos is not None and len(args) > data_arg_pos:
            data = args[data_arg_pos]
        else:
            data = None
        if logger is not None:
            logger.debug(f'{event}: {data}')
        if data is not None:
            args = args[:data_arg_pos] + (json.loads(data), ) + args[data_arg_pos + 1:]
        return dict_handler(*args)
    return _handler


class DictHandlerInterface(object):
    def on(
            self,
            event: str,
            dict_handler: Optional[Callable[[str, Dict], None]]=None,
            *, logging=False, # whether to log `event: data`
            is_dict_handler=False, # whether the `handler` handles dict
            data_arg_pos=None, # position of `data` in `handler` (starts from `0`). `None` if `data` is not passed, `None` also dismisses arg:`dict_handler`
            **kwargs
    ):
        def get_handler(dict_handler):
            return dict_handler if not is_dict_handler else unpack(
                event,
                dict_handler,
                self.logger if logging else None,
                data_arg_pos
            )
        on = super().on
        def set_handler(dict_handler):
            return on(
                event,
                get_handler(dict_handler),
                **kwargs
            )
        if dict_handler is None:
            return set_handler
        return on(event, get_handler(dict_handler), **kwargs)

    def emit(self, event: str, data: Dict=None, **kwargs):
        return super().emit(event, json.dumps(data) if data is not None else None, **kwargs)

    def __getattr__(self, name):
        if name not in ('json_on', 'json_event'):
            return super().__getattr__(name)

        def _json(*args, **kwargs):
            if 'data_arg_pos' not in kwargs:
                kwargs['data_arg_pos'] = self.DEFAULT_DATA_ARG_POS
            return getattr(self, name.split('_', 1)[1])(*args, is_dict_handler=True, **kwargs)

        return _json


class JsonClient(DictHandlerInterface, Client):
    DEFAULT_DATA_ARG_POS = 0


class JsonServer(DictHandlerInterface, Server):
    DEFAULT_DATA_ARG_POS = 1
