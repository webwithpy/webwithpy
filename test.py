from webwithpy.orm2 import DB, Table, Field
from webwithpy import run_server
from webwithpy.routing import GET


class TestTable(Table):
    table_name = "test_table"
    name = Field("string")


db = DB("sqlite:/test.db")


@GET("/")
def test_db():
    return ((db.test_table.name == "hello") | (db.test_table.name == "hello2")).select()


if __name__ == "__main__":
    db.create_table(TestTable)
    run_server()
