# The templating engine
The htpyp parser.

---

## accessing back-end variables
Whenever you have something like a user-name to send it with the html page to reduce overall post request being sent to
the server. This can be done with the pyht parser like this:

main.py:
```python
from webwithpy import run_server
from webwithpy.routing import ANY

@ANY(url='/', template='templates/user.html')
def hello_world():
    return dict(user_name="John Doe")

if __name__ == '__main__':
    run_server()
```

templates/user.html:
```html
<h1> {{=username}} </h1>
```

whenever going to the default webpage you will see in bold John Doe on your screen. this is ofcourse a pretty simple
example however you can send any variable to the front-end and even perform python functions on it. for example:

templates/user.html:
```html
{{if username == "John Doe":}} 
<h1> {{=username}} </h1>
{{pass}}
```

Now it will only show the username whenever it is John Doe.

---

## running python
With the templating system it's possible to run python code in html. This is made, so you can change the html based on 
what your controller gave you as seen in this example:
```html
{{if username == "John Doe":}} 
<h1> Hello {{=username}}! </h1>
{{else:}}
<h1> Welcome {{=username}}! </h1>
{{pass}}
```
as you can see in this example the program will only say Hello whenever the username is John Doe, This will allow you to
easily change your view based on variables.

---

## html blocks
The Htpyp parser also allows for html blocks, imagine you have a block of html that you might want to use multiple times,
but you really don't want to clutter up the code. This is the reason for html blocks!
Here's a pretty simple example of how to use them:
```html
{{block 'hello_world'}}
Hello World!
{{end}}
{{=hello_world}}
{{=hello_world}}
```

Where the output will simpy be:
```html
Hello World!
Hello World!
```

---

## Including files
Currently, Including and extending files do the same thing, however this might change in the near future.
However, for now it is recommended to use the `extends 'file_name'`!
As you can see it is pretty simple to extend any file using this, here are a couple of examples:
```html
{{extends 'templates/hello_world.html'}}
{{extends 'static/data.json'}}
```

Note that whenever you are extending files it will search for them from the root directory, this is designed this way
due to you not always only want to bw able to include child files and you sometimes also want to include parent files.

