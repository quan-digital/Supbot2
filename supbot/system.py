"""
system.py

provides services to different systems of supbot,
contains `System` class
"""

import logging
import threading
import typing
from typing import Tuple
from supbot import looper
from supbot.model import ActionBuffer, Event

if typing.TYPE_CHECKING:
    from supbot.api import Supbot


class System:
    """
    maintains shared states, and makes different states work together,
    provides interface to `Supbot` to control internal systems of supbot
    """

    def __init__(self, supbot: 'Supbot', device_name: str):
        """
        Initialize shared states: action buffer, logger, status, which is used for different systems to comunicate
        initializes looper thread
        :param supbot: reference for the `Supbot` object, used to retrieve events at runtime
        """
        logging.getLogger("selenium").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)

        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger("supbot")

        self._action_buffer: ActionBuffer = []
        self._logger = logger
        self._status = True
        self._looper_thread = threading.Thread(target=looper.start, args=(self, device_name))
        self._supbot = supbot

    @property
    def logger(self):
        """
        Provides logging services
        :return: logger object
        """
        return self._logger

    @property
    def action_buffer(self) -> ActionBuffer:
        """
        Provides action buffer,
        Used to add actions in the queue by `Supbot`,
        used to get actions to perform by `looper.py`
        :return: ActionBuffer object (list of actions)
        """
        return self._action_buffer

    def start(self):
        """
        Starts the looper thread,
        used by `Supbot` to start its services (to make them usable)
        """
        self._looper_thread.start()

    def wait_for_finish(self):
        """
        Waits for the looper thread to finish,
        looper thread finishes when,  `_status` flag is False and there are no actions left in `_action_buffer`
        """
        self._looper_thread.join()

    def quit(self):
        """
        Turns `_status` flag False
        used to tell other systems, that supbot has to be turned off
        """
        self._status = False

    def call_event(self, event: Event, params: Tuple):
        """
        Used to internal part of supbot to call events
        :param event: model.Event enum value
        :param params: data send for the event
        """
        callback = self._supbot.events[event]
        if callback is not None:
            callback(*params)

    def is_on(self) -> bool:
        """
        Used to check `_status` flag
        :return: `_status` flag
        """
        return self._status
