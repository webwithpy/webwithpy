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