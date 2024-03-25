# Guide to webwithpy grids
## Sql grids
SQL grids are a big part of webwithpy, they allow you to easily add, edit and delete rows
from any sql table in the database. Here is a simple use example of how to use grids with webwithpy:
```python
from webwithpy.orm import DB, Table, Field
from webwithpy.html import SQLForm
from webwithpy.routing import GET
from webwithpy import run_server

class Permission(Table):
    table_name = "permission"    
    user_id = Field("integer")   
    permission_level = Field("integer")

    
# edit_permission function will need to be able to access db(recommended to store as a class variable)
db = DB("sqlite:/storage.sqlite")
    
@GET('/')
def edit_permission():
    return SQLForm(db.permission).as_html()
    

if __name__ == "__main__":
    db.create_tables(Permission)
    run_server()
```

## Input Forms
With webwithpy you might not always want to use grids as you forms, for example with a login page or something users
aren't privileged to view. Here comes input forms which only allow users to submit to a form.
Here's an example of how to use an input form.

```python
from webwithpy.orm import DB, Table, Field
from webwithpy.html import InputForm
from webwithpy.routing import GET
from webwithpy import run_server

class Permission(Table):
    table_name = "permission"    
    user_id = Field("integer")   
    permission_level = Field("integer")

    
# edit_permission function will need to be able to access db(recommended to store as a class variable)
db = DB("sqlite:/storage.sqlite")
    
@GET('/')
def edit_permission():
    return InputForm(db.permission).__str__()
    

if __name__ == "__main__":
    db.create_tables(Permission)
    run_server()
```

As you can see the code looks pretty similar, however there is 1 thing to note! InputForms do NOT submit to the 
database. This means that whenever someone presses submit on the form nothing in the database will happen.
You may ask well how do I get the submitted form then? well it's quite easy shown in the example below:

```python
from webwithpy.orm import DB, Table, Field
from webwithpy.html import InputForm
from webwithpy.routing import GET
from webwithpy import run_server

class Permission(Table):
    table_name = "permission"    
    user_id = Field("integer")   
    permission_level = Field("integer")

    
# edit_permission function will need to be able to access db(recommended to store as a class variable)
db = DB("sqlite:/storage.sqlite")
    
@GET('/')
def edit_permission():
    form = InputForm(db.permission)
    
    if form.accepted:
        print(form.form_data)
    
    return form.__str__()
    

if __name__ == "__main__":
    db.create_tables(Permission)
    run_server()
```

As you can see we can find out if someone submitted the form to the webserver and then print out the data from the form.
<br>
### Since v0.7.1
SQLGrids and Input forms now fully support file uploads, here is an example of how to upload a file to a file and save
it server-side.

Note: For this it is recommended you use PIL for saving images

```python
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

```