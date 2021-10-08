from typing import Callable
from abc import ABC
import os


def clear_screen():
    if os.name == "posix":
        os.system("clear")
    else:
        os.system("cls")

class StateObservable(ABC):
    """
    Defines an interface for dependants to subscribe to state events.
    """
    __listeners : list[Callable]

    def __init__(self):
        self.__listeners = []

    def register_listener(self, callback : Callable):
        """Registers a callback to be invoked when the event is triggered.

        Arguments:
            callback {Callable} -- the callback function to invoke
        """        
        self.__listeners.append(callback)
    
    def trigger_state_event(self):
        """Triggers the event. Any objects registered to the event will have their respective callbacks invoked.
        """     
        for callback in self.__listeners:
            callback()