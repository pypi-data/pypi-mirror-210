from abc import ABC, abstractmethod
from typing import Any

from django.contrib.sessions.backends.base import SessionBase
from django.contrib.sessions.backends.db import SessionStore

from splathash.data.input_data import InputData


class ApplicationContext(ABC):
    """The context holds the application state"""

    @abstractmethod
    def initialize(self, data: dict) -> None:
        """
        Begin or resume the user's session using the incoming data
        from the USSD service provider.
        """

    @abstractmethod
    def update(self, key: str, value: Any) -> None:
        """Place some data in the context as a key value pair"""

    @abstractmethod
    def retrieve(self, key: str, default: Any = None) -> Any:
        """Retrieve data from the context"""

    @abstractmethod
    def next(self, route: str = None) -> str:
        """Set and retrieve the next route"""

    @abstractmethod
    def input_data(self) -> InputData:
        """Get current input data"""

    @abstractmethod
    def dispose(self) -> None:
        """Destroy user's session"""

    @abstractmethod
    def getData(self) -> str:
        """Get the current user entered data/response"""

    @abstractmethod
    def network(self) -> str:
        """Get the user's network"""

    @abstractmethod
    def msisdn(self) -> str:
        """Get the user's msisdn"""


class SessionBasedNALOApplicationContext(ApplicationContext):
    """Cater to NALO specific data format, using django db session"""

    __NEXT = "__NEXT"
    _store: SessionBase
    data: InputData

    def initialize(self, data: dict) -> None:
        """Place current data in the context"""
        self.data = InputData(
            msisdn=data["MSISDN"],
            network=data["NETWORK"],
            data=data["USERDATA"],
            start=data["MSGTYPE"],
            user=data["USERID"],
        )

        """ Create or retrieve session """
        key = self.data.msisdn
        self._store = SessionStore(session_key=key)

        """ Clear session if this is the start """
        if self.data.start:
            if not self._store.exists(session_key=key):
                self._store.save(must_create=True)
            self._store.clear()

    def update(self, key: str, value: Any) -> None:
        self._store[key] = value
        self._store.save()

    def retrieve(self, key: str, default: Any = None) -> Any:
        return self._store.get(key=key, default=default)

    def next(self, route: str = None) -> str:
        if route is None:
            return "{}".format(self.retrieve(key=self.__NEXT) or "")

        self.update(key=self.__NEXT, value=route)
        return route

    def input_data(self) -> InputData:
        return self.data

    def dispose(self) -> None:
        self._store.clear()
        self._store.delete()

    def getData(self) -> str:
        return self.data.data

    def network(self) -> str:
        return self.data.network

    def msisdn(self) -> str:
        return self.data.msisdn


class ApplicationContextFactory:
    @staticmethod
    def default() -> ApplicationContext:
        return SessionBasedNALOApplicationContext()
