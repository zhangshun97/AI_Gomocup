score = {
    'ONE': 10,
    'TWO': 100,
    'THREE': 1000,
    'FOUR': 100000,
    'FIVE': 10000000,
    'BLOCKED_ONE': 1,
    'BLOCKED_TWO': 10,
    'BLOCKED_THREE': 100,
    'BLOCKED_FOUR': 10000
}

threshold = 1.15


def equal(a, b):
    b = b if b else 0.01
    return (a >= b / threshold) and (a <= b * threshold) if b >= 0 else (a >= b * threshold) and (a <= b / threshold)


def greatThan(a, b):
    return a >= (b + 0.1) * threshold if b >= 0 else a >= (b + 0.1) / threshold


def greatOrEqualThan(a, b):
    return equal(a, b) or greatThan(a, b)


def littleThan(a, b):
    return a <= (b - 0.1) / threshold if b >= 0 else a <= (b - 0.1) * threshold


def littleOrEqualThan(a, b):
    return equal(a, b) or littleThan(a, b);
