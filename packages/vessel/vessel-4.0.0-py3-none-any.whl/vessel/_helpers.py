import functools


__all__ = ()


class Theme:

    def __init__(self):

        self._store = []

    def add(self, function):

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            for roster, subkwargs in self._store:
                if not function in roster:
                    continue
                break
            else:
                subkwargs = None
            if not subkwargs is None:
                kwargs = subkwargs | kwargs
            return function(*args, **kwargs)
        
        return wrapper
    
    def __call__(self, function, **kwargs):

        roster = {function}

        if isinstance(function, type):
            roster.add(function.__new__)
            roster.add(function.__init__)

        self._store.insert(0, (roster, kwargs))

        return self
    
    def __enter__(self, *args, **kwargs):

        pass

    def __exit__(self, *args, **kwargs):

        del self._store[0]
