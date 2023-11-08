cdef dict[str, dict[str, str]] _cache = {}

def insert_cache(str table_name, str select_stmt, list[str] value):
    _cache[table_name] = {select_stmt: value}

def get_cache_by_select(str table_name, str select_stmt):
   return _cache.get(table_name, {}).get(select_stmt, None)

def remove_table_cache(str table_name):
    global _cache
    _cache = {k: v for k, v in _cache.items() if table_name not in k}

def print_cache():
    print(_cache)