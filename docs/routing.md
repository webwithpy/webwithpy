# The routing system
The routing system explained

---

Currently, the routing system is pretty simple due to not being fully developed yet.
For now the only thing routes can do are accept GET or POST request or both, here are a couple examples

```python
from webwithpy.routing import GET, POST, ANY
from random import Random

@GET('/')
def index():
    return "Hello Users"

@POST('/random_bytes')
def random_bytes():
    return Random().randbytes(100)

@ANY('/random_int')
def random_integer():
    return Random().randint(0, 1000)
```

As you can see above, if you go now to the set port and go to '/', '/random_bytes' or '/random_int' it will run the 
code by the path.

