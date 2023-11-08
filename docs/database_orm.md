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

### smart caching
Sqp will create and remove items from the cache based on previous queries made. Caching is incredibly useful to use
whenever you have a huge select query, or you need to do a query alot of times. The caching will be removed for a 
specific table whenever you update or delete items from the table. In the future this is aimed to be improved where only
some queries will be uncached when a update or delete stmt is done

### fields
In sqp fields are a pythonic representation of what the fields look like in a database.

#### field types

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

## creating queries
In sqp it's pretty simple to create a query, this an example query on the User table we've created above.

```python
from webwithpy.orm import DB, Table, Field

class User(Table):
    table_name = "user"
    first_name = Field("string")
    last_name = Field("string")

db = DB("sqlite:/storage.db")    
query = (db.user.first_name == "John Doe")
```

The query we've made below will check for every row in User if User.first_name == "John Doe"
under here is every possible query you can make in webwithpy(list of all the operators)

```python
from webwithpy.orm import DB, Table, Field

class User(Table):
    table_name = "user"
    first_name = Field("string")
    last_name = Field("string")
    
db = DB("sqlite:/storage.db")
query = (db.user.first_name == "John Doe")
query = (db.user.id < 10)
query = (db.user.id > 0)
query = (db.user.id <= 10)
query = (db.user.id >= 0)
```

#### adding queries together
to make multiple queries in 1 user the '&' operator.

```python
query = ((db.user.id >= 0) & (db.user.id <= 10))
```

## inserting fields
There is currently only 1 way to insert values into the table, To do this you will need to do `db.table.insert()`.
when using this you will need to add parameters based on the tables fields ea: `db.table.insert(first_name='John')`.
Under here is a example of inserting fields.
```python
from webwithpy.orm import DB, Table, Field

class User(Table):
    table_name = "user"
    first_name = Field("string")
    last_name = Field("string")
    
db = DB("sqlite:/storage.db")
db.user.insert(first_name="John Doe", last_name="doos")
```
You don't need to include all the fields when inserting

## selecting fields
There are multiple ways to select fields from a table, the easiest way is to use `Table.select()`.<br>
This will select all the fields from the table, however if you only want to select specific fields from the table
you will need to make queries. This is a example of how to select a field based on any query:

```python
selected_fields = (db.user.id < 10).select()
```

This will select all fields from the database that have an id that has a value that is less than 10!

## updating fields
The only way to update fields is to create a query and type the variables you want to change, for example:

```python
(db.user.id < 10).update(first_name="user")
```

Note that the only thing that isn't recommended to change is the table's id!

## deleting fields
Removing fields from the table works very similar to updating fields in the table, however you don't need to give up
the fields you want to change because you are removing them. Below here is a simple example of how to remove fields from
an table

```python
(db.user.id < 10).delete()
```