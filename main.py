import enum
import sys

from astropy.time import Time
import astropy.units as u
import numpy as np


class Season(enum.Enum):
    SPRING = 0
    SUMMER = 1
    AUTUMN = 2
    WINTER = 3


def table_jde_0(season, year):
    assert 1000 <= year <= 3000
    y = (year - 2000) / 1000
    match season:
        case Season.SPRING:
            return (
                2451623.80984 + 365242.37404 * y + 0.05169 * y**2
                - 0.00411 * y**3 - 0.00057 * y**4
            )
        case Season.SUMMER:
            return (
                2451716.56767 + 365241.62603 * y + 0.00325 * y**2
                + 0.00888 * y**3 - 0.00030 * y**4
            )
        case Season.AUTUMN:
            return (
                2451810.21715 + 365242.01767 * y - 0.11575 * y**2
                + 0.00337 * y**3 + 0.00078 * y**4
            )
        case Season.WINTER:
            return (
                2451900.05952 + 365242.74049 * y - 0.06223 * y**2
                - 0.00823 * y**3 + 0.00032 * y**4
            )
        case _:
            assert False, 'unreachable'


def read_table_23c():
    data = np.loadtxt('table_23c.txt', dtype=np.float64, skiprows=6)
    data = data.reshape((12, 6))
    a = np.hstack((data[:, 0], data[:, 3]))
    b = np.hstack((data[:, 1], data[:, 4])) * u.degree
    c = np.hstack((data[:, 2], data[:, 5])) * u.degree
    return a, b, c


def do_computation(season, year):
    jde_0 = table_jde_0(season, year)
    t = (jde_0 - 2451545.0) / 36525
    w = (35999.373 * u.deg) * t - (2.47 * u.deg)
    dl = 1 + 0.0334 * np.cos(w) + 0.0007 * np.cos(2*w)
    a, b, c = read_table_23c()
    s = np.sum(a * np.cos(b + c * t))
    jde = jde_0 + (0.00001 * s) / dl
    time = Time(jde * u.day, format='jd')
    time.format = 'isot'
    return time


def main(year):
    
    # Need previous winter solstice for figuring out February cross-quarter
    prev_winter = do_computation(Season.WINTER, year - 1)

    # This year's solstices and equinoxes
    spring = do_computation(Season.SPRING, year)
    summer = do_computation(Season.SUMMER, year)
    autumn = do_computation(Season.AUTUMN, year)
    winter = do_computation(Season.WINTER, year)

    # This year's cross-quarter holidays
    feb = prev_winter + (spring - prev_winter) / 2
    may = spring + (summer - spring) / 2
    aug = summer + (autumn - summer) / 2
    nov = autumn + (winter - autumn) / 2

    print('SOLSTICES, EQUINOXES, AND CROSS-QUARTERS')
    print(f'Year: {year}')
    print()
    print(f'   Cross: {feb!s}')
    print(f'  Spring: {spring!s}')
    print(f'   Cross: {may!s}')
    print(f'  Summer: {summer!s}')
    print(f'   Cross: {aug!s}')
    print(f'  Autumn: {autumn!s}')
    print(f'   Cross: {nov!s}')
    print(f'  Winter: {winter!s}')


if __name__ == '__main__':
    _, arg_1 = sys.argv
    main(int(arg_1))
