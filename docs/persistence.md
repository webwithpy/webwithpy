# Webwithpy's persistence manager
## Example: Page Viewed Counter

This example demonstrates how to implement a simple counter that increments each time a user visits the homepage.


```python
from webwithpy import PersistenceManager
from webwithpy.routing import GET
from webwithpy import run_server


@GET("/")
def page_viewed_counter():
    if isinstance(PersistenceManager.get_item("counter"), bool):
        PersistenceManager.set_item("counter", 1)
    else:
        PersistenceManager.set_item(
            "counter", PersistenceManager.get_item("counter") + 1
        )

    return f'counter: {PersistenceManager.get_item("counter")}'


if __name__ == "__main__":
    run_server()

```

## Best Practices

- **Use descriptive keys**: When using `set_item` and `get_item`, choose keys that clearly describe the data being stored. This makes your code more readable and maintainable.
- **Handle exceptions**: Consider handling potential exceptions that might occur during data retrieval or storage. This can help in debugging and ensuring a more robust application.
- **Consider data types**: Be mindful of the data types you're storing. The Persistence Manager stores data as strings, so you may need to convert between strings and other types when retrieving data.

## Conclusion

The `webwithpy` Persistence Manager simplifies the process of storing and retrieving user-specific data. By following this guide, you can easily integrate persistence into your web applications, enhancing user experience and data retention.
