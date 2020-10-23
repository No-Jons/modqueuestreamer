import random


def create_code():
    return "".join([str(random.choice(range(0, 9))) for i in range(6)])


def is_int(to_test: str):
    try:
        new = int(to_test)
        return new
    except ValueError:
        return False
