from .app import App

from typing import Dict, List, Any
from uuid import UUID


class PersistenceManager:
    _persistence: dict[UUID, Dict[str, Any]] = {}

    @classmethod
    def set_item(cls, name: str, value: Any) -> None:
        """saves items with the user, currently only stores for 1 day!"""
        uid: UUID = App.response.get_cookie("session")

        if uid not in cls._persistence:
            cls._persistence[uid] = {}

        PersistenceManager._persistence[uid][name] = value

    @classmethod
    def get_item(cls, name: str) -> Any | bool:
        """Gets the item that is saved with the user"""

        # get the current user session
        uid: UUID = App.response.get_cookie("session")
        if uid in cls._persistence:
            return PersistenceManager._persistence[uid][name]

        return False

    @classmethod
    def clear_item(cls, name: str) -> None:
        """clears any set item if it is stored"""
        uid: UUID = App.response.get_cookie("session")
        if uid in cls._persistence:
            del cls._persistence[uid][name]
