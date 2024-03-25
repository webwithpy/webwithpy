from webwithpy.orm.auth import Auth
from webwithpy.routing import Router, Route, ANY
from webwithpy.html import InputForm
from webwithpy.orm import DB, Table, Field
from webwithpy import run_server


class Video(Table):
    table_name = "video"
    video_name = Field("string")
    video_description = Field("string")
    url = Field("reference video_url.url")
    uploaded_by = Field("reference auth_user.first_name")


class VideoUrl(Table):
    table_name = "video_url"
    url = Field("string")


class Temp(Table):
    table_name = "temp"
    name = Field("string")
    upload = Field("image")


db = DB("sqlite:/test.db")
# db = DB("mysql:/|sammy:helloWorld9!@localhost/wwp")


def test():
    form = InputForm(db.temp, "test")

    return form


def test2():
    return "Hello World"


Router.bulk_add_routes(Route(test, "/", "ANY"), Route(test2, "/test", "GET"))

if __name__ == "__main__":
    db.create_tables(VideoUrl, Video, Temp)
    auth = Auth(pretty_form=True)
    run_server()
