cdef dict[str, dict[str, str]] _cache = {}

def insert_cache(str table_name, str select_stmt, list[str] value):
    _cache[table_name] = {select_stmt: value}

def get_cache_by_select(str table_name, str select_stmt):
   return _cache.get(table_name, {}).get(select_stmt)

def select_in_cache(str table_name, str select_stmt):
   return table_name in _cache and select_stmt in _cache[table_name]

def remove_table_cache(str table_name):
   _cache.pop(table_name)