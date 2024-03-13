from webwithpy.orm import DB, Table, Field
from webwithpy import run_server
from webwithpy.routing import GET


class Test(Table):
    table_name = "test"
    x = Field("int")


class Test2(Table):
    table_name = "test2"
    y = Field("int")


# db = DB("sqlite:/test.db")
db = DB("mysql:/|sammy:helloWorld9!@localhost/wwp")


@GET("/")
def test():
    return "Hello World!"


if __name__ == "__main__":
    db.create_tables(Test, Test2)
    # ((db.test.id > 1) & (db.test2.id > 1)).select()
    db.test.insert(x=1)
    print((db.test.id == 1).select())
    run_server()
