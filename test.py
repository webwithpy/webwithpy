from webwithpy.routing import ANY
from webwithpy.html import InputForm
from webwithpy.orm import DB, Table, Field
from webwithpy import run_server
from PIL import Image
from io import BytesIO

db = DB("sqlite:/test.db")


class Test(Table):
    table_name = "test"
    name = Field("string")
    upload = Field("image")


@ANY("/")
def upload():
    form = InputForm(db.test, form_title="upload")

    if form.accepted:
        img = Image.open(BytesIO(form.form_data["upload"]))
        img.save("test.png")

    return form


if "__main__" == __name__:
    db.create_table(Test)
    run_server()
