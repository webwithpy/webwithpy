from webwithpy.orm.dialects.sql import SQLDialect


class MysqlDialect(SQLDialect):
    def insert(self, table_name: str, items: dict):
        return f"INSERT INTO {table_name} ({','.join(items.keys())}) VALUES ({','.join(['?' for _ in items.keys()])})"

    def select(self, fields, tables, where=None, distinct=None, orderby=None):
        return f"SELECT {distinct}{fields} FROM {tables}{where}{orderby}"

    def update(self, first_table: str, update_vals: str, where: str):
        return f"UPDATE {first_table} SET {update_vals} {where}"

    def delete(self, first_table: str, select: str):
        return f"DELETE FROM {first_table} {select}"
