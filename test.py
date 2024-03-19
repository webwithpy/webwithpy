from webwithpy.routing import Router, Route, ANY
from webwithpy.html import SQLForm
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


db = DB("sqlite:/test.db")
# db = DB("mysql:/|sammy:helloWorld9!@localhost/wwp")


def test():
    return SQLForm((db.test.id > 0), fields=[db.test.x]).as_html()


def test2():
    return "Hello World"


Router.bulk_add_routes(Route(test, "/", "ANY"), Route(test2, "/test", "GET"))

if __name__ == "__main__":
    db.create_tables(VideoUrl, Video)
    run_server()
