import random


def randint_normal(a, b, mean, std_dev):
    x = int(random.normalvariate(mean, std_dev))
    x = abs(x)
    x = min(b, max(a, x))
    return x


def random_bool(true_prob):
    return random.choices([True, False], weights=[true_prob, 1 - true_prob], k=1)[0]


def shuffled_bools(size, true_percent):
    true_num = int(size * true_percent)
    bools = [True for _ in range(true_num)] + [False for _ in range(size - true_num)]
    random.shuffle(bools)
    return bools
