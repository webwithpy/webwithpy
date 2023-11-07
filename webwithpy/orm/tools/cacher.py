from typing import Any


class Cacher:
    _cache: dict[str, dict[str, Any]] = {}

    @classmethod
    def insert_cache(cls, table_name, select_stmt, value):
        Cacher._cache[table_name] = {select_stmt: value}

    @classmethod
    def get_cache_by_select(cls, table_name: str, select_stmt: str):
        return Cacher._cache.get(table_name, {}).get(select_stmt)

    @classmethod
    def select_in_cache(cls, table_name: str, select_stmt: str):
        return Cacher._cache.get(table_name, None) is not None and (
            Cacher._cache.get(table_name).get(select_stmt, None) is not None
        )

    @classmethod
    def remove_table_cache(cls, table_name: str):
        Cacher._cache.pop(table_name)