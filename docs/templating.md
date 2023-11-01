# The templating engine
The pyht parser.

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