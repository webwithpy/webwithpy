import asyncio


class HandleAsync:
    @classmethod
    async def call_function(cls, func, *args, **kwargs):
        if cls.is_async(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)

    @classmethod
    def is_async(cls, func):
        return asyncio.iscoroutinefunction(func)
