import random


def create_code():
    return "".join([str(random.choice(range(0, 9))) for i in range(6)])
