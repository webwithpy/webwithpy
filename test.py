from webwithpy.routing import Router, Route, ANY
from webwithpy.html import SQLForm
from webwithpy.orm import DB, Table, Field
from webwithpy import run_server


class Test(Table):
    table_name = "test"
    x = Field("int")


class Test2(Table):
    table_name = "test2"
    y = Field("int")


# db = DB("sqlite:/test.db")
db = DB("mysql:/|sammy:helloWorld9!@localhost/wwp")


def test():
    return SQLForm((db.test.id > 0), fields=[db.test.x]).as_html()


def test2():
    return "Hello World"


Router.bulk_add_routes(Route(test, "/", "ANY"), Route(test2, "/test", "GET"))

if __name__ == "__main__":
    db.create_tables(Test, Test2)
    # ((db.test.id > 1) & (db.test2.id > 1)).select()
    run_server()
