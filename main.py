import datetime as dt
import enum
import sys
import zoneinfo

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
    b = np.hstack((data[:, 1], data[:, 4]))
    c = np.hstack((data[:, 2], data[:, 5]))
    return a, b, c


def jd_to_dt(jd):
    jd += 0.5
    z = int(jd)
    f = jd - z
    if z < 2299161:
        a = z
    else:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - int(alpha / 4)
    b = a + 1524
    c = int((b - 121.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    day_with_decimals = b - d - int(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715

    day = int(day_with_decimals)
    day_fraction = day_with_decimals - day

    hour_with_decimals = 24 * day_fraction
    hour = int(hour_with_decimals)
    hour_fraction = hour_with_decimals - hour

    minute_with_decimals = 60 * hour_fraction
    minute = int(minute_with_decimals)
    minute_fraction = minute_with_decimals - minute

    second_with_decimals = 60 * minute_fraction
    second = int(second_with_decimals)
    second_fraction = second_with_decimals - second

    microsecond = round(1_000_000 * second_fraction)

    return dt.datetime(
        year, month, day, hour, minute, second, microsecond,
        tzinfo=zoneinfo.ZoneInfo('UTC'),
    )


def do_computation(season, year):
    jde_0 = table_jde_0(season, year)
    t = (jde_0 - 2451545.0) / 36525
    w_degrees = 35999.373 * t - 2.47
    w_radians = np.radians(w_degrees)
    dl = 1 + 0.0334 * np.cos(w_radians) + 0.0007 * np.cos(2 * w_radians)
    a, b_degrees, c_degrees = read_table_23c()
    s = np.sum(a * np.cos(np.radians(b_degrees + c_degrees * t)))
    jde = jde_0 + (0.00001 * s) / dl
    return jd_to_dt(jde)


def main(year, utc=''):
    year = int(year)
    assert utc in ('', 'utc')

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

    if utc:
        tz = zoneinfo.ZoneInfo('UTC')
    else:
        tz = zoneinfo.ZoneInfo('localtime')

    print('SOLSTICES, EQUINOXES, AND CROSS-QUARTERS')
    print(f'  Input Year: {year}')
    print(f'   Time Zone: {"UTC" if utc else "local"}')
    print()
    print(f'     Cross: {feb.astimezone(tz)!s}')
    print(f'    Spring: {spring.astimezone(tz)!s}')
    print(f'     Cross: {may.astimezone(tz)!s}')
    print(f'    Summer: {summer.astimezone(tz)!s}')
    print(f'     Cross: {aug.astimezone(tz)!s}')
    print(f'    Autumn: {autumn.astimezone(tz)!s}')
    print(f'     Cross: {nov.astimezone(tz)!s}')
    print(f'    Winter: {winter.astimezone(tz)!s}')
    print()


if __name__ == '__main__':
    _, *args = sys.argv
    main(*args)
