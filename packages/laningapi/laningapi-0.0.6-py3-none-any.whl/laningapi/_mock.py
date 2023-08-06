import functools

mocking = {}


class Mock:
    def __init__(self, module, method):
        self.module = module.lower()
        self.method = method.lower()

    def __enter__(self):
        mocking[(self.module, self.method)] = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        mocking.pop((self.module, self.method))

    def register(self, returns):
        mocking[(self.module, self.method)] = returns


def mock_decorator(module, func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (module.lower(), func.__name__.lower())
        mock_res = mocking.get(key)
        if mock_res:
            return mock_res
        return func(*args, **kwargs)

    return wrapper


class MockType(type):
    def __new__(mcs, clsname, bases, dct):
        for name, member in dct.items():
            if callable(member) and not name.startswith("__"):
                dct[name] = mock_decorator(clsname, member)
        return super().__new__(mcs, clsname, bases, dct)
