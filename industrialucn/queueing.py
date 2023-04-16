import numpy as np


def mm1(arrival, departure):
    rho = arrival / departure
    po = 1 - rho
    nqueue = rho ** 2 / (1 - rho)
    nsis = nqueue + rho
    tqueue = nqueue / arrival
    tsis = nsis / arrival

    return rho, po, nqueue, nsis, tqueue, tsis


def mm1prob(arrival, departure, j):
    rho = arrival / departure
    po = 1 - rho
    pj = rho ** j * po

    return po, pj


def mms(arrival, departure, s):
    rho = arrival / (s * departure)

    po = 1 / (sum(1 / np.math.factorial(i) * (arrival / departure) ** i for i in range(s)) + (
            arrival / departure) ** s / (np.math.factorial(s) * (1 - rho)))

    nqueue = po * (arrival / departure) ** s * rho / (np.math.factorial(s) * (1 - rho) ** 2)
    nsis = nqueue + arrival / departure
    tqueue = nqueue / arrival
    tsis = nsis / arrival

    return rho, po, nqueue, nsis, tqueue, tsis


def mmsprob(arrival, departure, s, j):
    rho = arrival / (s * departure)

    po = 1 / (sum(1 / np.math.factorial(i) * (arrival / departure) ** i for i in range(s)) + (
            arrival / departure) ** s / (np.math.factorial(s) * (1 - rho)))

    if j <= s:
        pj = po * (arrival / departure) ** j / (np.math.factorial(j))
    else:
        pj = po * s ** s * (arrival / (s * departure)) ** j / (np.math.factorial(s))

    return po, pj


def mm1k(arrival, departure, k):
    rho = arrival / departure

    po = (1 - rho) / (1 - rho ** (k + 1))
    pk = rho ** k * po
    lambda_ef = arrival * (1 - pk)

    nqueue = rho / (1 - rho) - (rho + k * rho ** (k + 1)) / (1 - rho ** (k + 1))
    nsis = nqueue + lambda_ef / departure
    tqueue = nqueue / lambda_ef
    tsis = nsis / lambda_ef

    return rho, po, pk, lambda_ef, nqueue, nsis, tqueue, tsis


def mm1kprob(arrival, departure, k, j):
    rho = arrival / departure

    po = (1 - rho) / (1 - rho ** (k + 1))
    pj = rho ** j * po

    return po, pj


def mmsk(arrival, departure, s, k):
    rho = arrival / (s * departure)

    po = 1 / (sum(1 / np.math.factorial(i) * (arrival / departure) ** i for i in range(s)) + (
            arrival / departure) ** s / (np.math.factorial(s)) * (1 - rho ** (k - s + 1)) / (1 - rho))

    if k <= s:
        pk = po * (arrival / departure) ** k / (np.math.factorial(k))
    else:
        pk = po * s ** s * (arrival / (s * departure)) ** k / (np.math.factorial(s))

    lambda_ef = arrival * (1 - pk)

    nqueue = po * (arrival / departure) ** s * rho / (np.math.factorial(s) * (1 - rho) ** 2) * (
            1 - rho ** (k - s) - (k - s) * rho ** (k - s) * (1 - rho))
    nsis = nqueue + lambda_ef / departure
    tqueue = nqueue / lambda_ef
    tsis = nsis / lambda_ef

    return rho, po, pk, lambda_ef, nqueue, nsis, tqueue, tsis


def mmskprob(arrival, departure, s, k, j):
    rho = arrival / (s * departure)

    po = 1 / (sum(1 / np.math.factorial(i) * (arrival / departure) ** i for i in range(s)) + (
            arrival / departure) ** s / (np.math.factorial(s)) * (1 - rho ** (k - s + 1)) / (1 - rho))

    if j <= s:
        pj = po * (arrival / departure) ** j / (np.math.factorial(j))
    else:
        pj = po * s ** s * (arrival / (s * departure)) ** j / (np.math.factorial(s))

    return po, pj


def mm1n(arrival, departure, n):
    rho = arrival / departure
    po = 1 / (
        sum(np.math.factorial(n) / np.math.factorial(n - i) * (arrival / (departure * n)) ** i for i in range(n + 1)))

    nsis = sum(i * np.math.factorial(n) / np.math.factorial(n - i) * (arrival / (departure * n)) ** i * po for i in
               range(n + 1))
    nqueue = nsis - arrival * (1 - po) / departure

    lambda_ef = arrival * (n - nsis)
    tqueue = nqueue / lambda_ef
    tsis = nsis / lambda_ef

    return rho, po, lambda_ef, nqueue, nsis, tqueue, tsis


def mm1nprob(arrival, departure, n, j):
    po = 1 / (
        sum(np.math.factorial(n) / np.math.factorial(n - i) * (arrival / (departure * n)) ** i for i in range(n + 1)))

    pj = np.math.factorial(n) / np.math.factorial(n - j) * (arrival / (departure * n)) ** j * po

    return po, pj


def mmsn(arrival, departure, s, n):
    rho = arrival / (s * departure)
    po = 1 / (sum(
        np.math.factorial(n) / (np.math.factorial(n - i) * np.math.factorial(i)) * (arrival / (departure * n)) ** i for
        i in range(0, s)) + s ** s / np.math.factorial(s) * sum(
        np.math.factorial(n) / np.math.factorial(n - i) * (arrival / (s * departure * n)) ** i for i in
        range(s, n + 1)))

    nsis = po * (arrival / departure * (1 + (arrival / (departure * n))) ** (n - 1) + sum(
        np.math.factorial(n) / np.math.factorial(n - j) * j * (
                s ** s / np.math.factorial(s) - s ** j / np.math.factorial(j)) * (arrival / (s * departure * n)) ** j
        for j in range(s, n + 1)))

    lambda_ef = arrival * (1 - nsis / n)
    nqueue = nsis - (arrival / departure) * (lambda_ef / arrival)
    tqueue = nqueue / lambda_ef
    tsis = nsis / lambda_ef

    return rho, po, lambda_ef, nqueue, nsis, tqueue, tsis


def mmsnprob(arrival, departure, s, n, j):
    po = 1 / (sum(
        np.math.factorial(n) / (np.math.factorial(n - i) * np.math.factorial(i)) * (arrival / (departure * n)) ** i for
        i in range(0, s)) + s ** s / np.math.factorial(s) * sum(
        np.math.factorial(n) / np.math.factorial(n - i) * (arrival / (s * departure * n)) ** i for i in
        range(s, n + 1)))

    if j <= s:
        pj = np.math.factorial(n) / (np.math.factorial(n - j) * np.math.factorial(j)) * (
                arrival / (departure * n)) ** j * po
    else:
        pj = np.math.factorial(n) / (np.math.factorial(n - j)) * (s ** s / np.math.factorial(s)) * (
                arrival / (s * departure * n)) ** j * po

    return po, pj
