import math


def get_distance(x1, y1, x2, y2):

    return norm(x2 - x1, y2 - y1)


def norm(*args):
    result = 0
    for x in args:
        result += x ** 2
    return math.sqrt(result)
