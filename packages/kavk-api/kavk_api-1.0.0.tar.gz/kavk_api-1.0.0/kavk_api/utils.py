from random import randint

def get_random_id() -> int:
    return randint(-2**31, (2**31)-1)

__all__ = ('get_random_id')
