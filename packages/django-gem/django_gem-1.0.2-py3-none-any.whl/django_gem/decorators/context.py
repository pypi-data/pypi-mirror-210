from django_gem.context import CuttingAlwaysEager


def cutting_always_eager(func):
    def inner_func(*args, **kwargs):
        with CuttingAlwaysEager():
            return func(*args, **kwargs)

    return inner_func
