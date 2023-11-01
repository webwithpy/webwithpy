# Guide to the sqp orm
easy guide to sqp

---

## connecting to the database
The most important thing for a orm is being able to connect ta a db, which is made extremely easy in webwithpy!

```python
from webwithpy.orm import DB

db = DB("sqlite:/storage.db")
```
NOTE SQLITE IS THE ONLY DB SUPPORTED RN!!

As you can see from the python script the database uses sqlite. you can give up the drive by doing a "driver:/"
where the driver is ofcourse the db you are using(postgres, sqlite, ect.). 

## creating tables
when starting with the webwithpy orm you will ofcourse need to define sql tables. This is done in webwithpy by 
subclassing the sqp table. Here is shown how to create simply create a user table with the sqp orm:

```python
from webwithpy.orm import Table, Field

class User(Table):
    table_name = "user"
    first_name = Field("string")
    last_name = Field("string")
```

This is one of the easiest way to create a table with sqp however it doesn't actually exist yet, so to actually define
the table we will need to create it like this:

```python
from webwithpy.orm import DB, Table, Field

class User(Table):
    table_name = "user"
    first_name = Field("string")
    last_name = Field("string")
    
db = DB("sqlite:/storage.db")
db.create_tables()
```

the function create tables will create tables based on classes that have subclassed the sqp Table

### field types
Under here is a table of all the table field types

| type     | py orm            |
|----------|-------------------|
| integer  | Field("int")      |
| string   | Field("string")   |
| float    | Field("float")    |
| boolean  | Field("bool")     |
| date     | Field("date")     |
| datetime | Field("datetime") |
| time     | Field("time")     |
| image    | Field("image")    |
<br>

## creating queries
In sqp it's pretty simple to create a query, this an example query on the User table we've created above.

```python
from webwithpy.orm import DB, Table, Field

class User(Table):
    first_name = Field("string")
    last_name = Field("string")

db = DB("sqlite:/storage.db")    
query = (db.user.first_name == "John Doe")
```

The query we've made below will check for every row in User if User.first_name == "John Doe"
under here is every possible query you can make in webwithpy(list of all the operators)

```python
from webwithpy.orm import Table, Field

class User(Table):
    first_name = Field("string")
    last_name = Field("string")
    
db = DB("sqlite:/storage.db")
query = (db.user.first_name == "John Doe")
query = (db.user.id < 10)
query = (db.user.id > 0)
query = (db.user.id <= 10)
query = (db.user.id >= 0)
```

### adding queries together
to make multiple queries in 1 user the '&' operator.

```python
query = ((db.user.id >= 0) & (db.user.id <= 10))
```

### selecting fields
There are multiple ways to select fields from a table, the easiest way is to use `Table.select()`.<br>
This will select all the fields from the table, however if you only want to select specific fields from the table
you will need to make queries. This is a example of how to select a field based on any query:

```python
selected_fields = (db.user.id < 10).select()
```

This will select all fields from the database that have an id that has a value that is less than 10