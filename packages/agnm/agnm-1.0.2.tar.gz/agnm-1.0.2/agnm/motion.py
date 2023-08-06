import math


def acceleration(v_delta=math.inf, t=math.inf, vf=math.inf, vi=math.inf):
    """
    Method, that calculates acceleration, using function, based on passed parameters
    a = v/t
    a = (vf+vi)/t

    :param v_delta: change in velocity (m/s)
    :param t: time (s)
    :param vf: final velocity (m/s)
    :param vi: initial velocity (m/s)
    :return: acceleration value or infinity if none of the passed arguments combinations match described functions
    """
    if v_delta != math.inf and t != math.inf:
        return v_delta / t
    elif vi != math.inf and vf != math.inf and t != math.inf:
        return (vf - vi) / t
    else:
        return math.inf


def v_average(x_delta=math.inf, t=math.inf, vf=math.inf, vi=math.inf):
    """
    Method, that calculates average velocity, using function, based on passed parameters
    va = x/t
    va = (vi+vf)/2

    :param x_delta: change in position (m)
    :param t: time (s)
    :param vf: final velocity (m/s)
    :param vi: initial velocity (m/s)
    :return: average velocity value or infinity if none of the passed arguments combinations match described functions
    """
    if x_delta != math.inf and t != math.inf:
        return x_delta / t
    elif vi != math.inf and vf != math.inf:
        return (vf - vi) / 2
    else:
        return math.inf


def v_final(vi, a, t=math.inf, x_delta=math.inf):
    """
    Method, that calculates final velocity, using function, based on passed parameters
    vf = (vi^2+2a*x)^1/2
    vf = vi+a*t

    :param vi: initial velocity (m/s)
    :param a: acceleration (m/s^2)
    :param t: time (s)
    :param x_delta: change in position (m)
    :return: final velocity value or infinity if none of the passed arguments combinations match described functions
    """
    if not vi or not a:
        return math.inf

    if t != math.inf:
        return vi + a * t

    if x_delta != math.inf:
        return vi ** 2 + 2 * a * x_delta

    return math.inf


def change_in_position(vi, t, a):
    """
    Method, that calculates change in position
    x = vi*t+1/2*a*t^2

    :param vi: initial velocity (m/s)
    :param t: time (s)
    :param a: acceleration (m/s^2)
    :return: change in position value
    """
    return vi * t + 0.5 * a * (t ** 2)


def displacement(t, vf, vi):
    """
    Method, that calculates displacement
    x = (vi-vf)/2*t

    :param t: time (s)
    :param vf: final velocity (m/s)
    :param vi: initial velocity (m/s)
    :return: displacement value
    """
    return 0.5 * (vi + vf) * t
