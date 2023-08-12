import queue


class DB(object):
    def __init__(self):
        self.__queue = queue.Queue()
        self.__locked = False

    def __getattribute__(self, item):
        attr = super().__getattribute__(item)

        if hasattr(attr, "__call__"):
            def interceptor(*args, **kwargs):
                self.__queue.put((attr, args, kwargs))
                while True:
                    if self.__locked:
                        # lock
                        continue
                    else:
                        self.__locked = True
                        rv = attr(*args, **kwargs)
                        self.__locked = False
                        return rv

            return interceptor
        else:
            return attr

    def test(self, x: int) -> int:
        return x+1
