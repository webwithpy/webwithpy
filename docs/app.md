# using requests with webwithpy
## The app class
Webwithpy version <1.0 will expose the inbound and outgoing requests to users(this goes also for the cookies the user 
has, path it accessed and more). Accessing the app is pretty simple shown below

```python
from webwithpy.routing import GET
from webwithpy import run_server, App

@GET('/')
def get_cookies():
    return App.response.get_all_cookies()

if __name__ == "__main__":
    run_server()
```

## The cookie jar
Webwithpy also comes with a build in cookie jar where you can add, remove and get cookies from.
Here is an example of how to do al 3 methods:

```python
from webwithpy.routing import GET
from webwithpy import run_server, App

@GET('/')
def get_cookies():
    # get all cookies
    cookies = App.response.get_all_cookies()
    # add a cookie
    App.response.add_cookie("value", 5)
    # get a cookie
    cookie = App.response.get_cookie("value")
    
    return cookie

if __name__ == "__main__":
    run_server()
```