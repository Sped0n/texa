from collections.abc import Callable
from typing import Literal

StateType = Literal[
    "wait for frontend",
    "no model",
    "initializing",
    "initialization failed",
    "inferencing",
    "inference failed",
    "idle",
]


class State:
    def __init__(self, state: StateType):
        self.__callbacks: list[Callable[[StateType], None]] = []
        self.__state: StateType = state

    def get(self) -> StateType:
        return self.__state

    def set(self, value: StateType) -> None:
        if value == self.__state:
            return
        self.__state = value
        for callback in self.__callbacks:
            callback(value)

    def add_callback(self, callback: Callable[[StateType], None]) -> None:
        self.__callbacks.append(callback)
