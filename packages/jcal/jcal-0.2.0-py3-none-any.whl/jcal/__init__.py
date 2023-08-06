import calendar as clndr
import datetime
import sys
from typing import Set


def holiday(year: int) -> set[datetime.date]:
    """日本の休日（2019-2023）

    :param year: Year
    :return: 休日（「国民の祝日に関する法律」第3条）の集合
             （同第1条の国民の祝日ではないことに注意）
    """
    res, t = [], datetime.timedelta(1)
    sp = int(20.8431 + 0.242194 * (year - 1980) - (int)((year - 1980) / 4))
    au = int(23.2488 + 0.242194 * (year - 1980) - (int)((year - 1980) / 4))
    hs = [(1, 1), (1, -2), (2, 11), (2, 23), (3, sp), (4, 29), (5, 3), (5, 4), (5, 5)]
    hs += [(7, -3), (8, 11), (9, -3), (9, au), (10, -2), (11, 3), (11, 23)]
    if year == 2019:
        hs = list(set(hs) - {(2, 23)} | {(5, 1), (10, 22)})
    elif year == 2020:
        hs = list(set(hs) - {(7, -3), (8, 11), (10, -2)} | {(7, 23), (7, 24), (8, 10)})
    elif year == 2021:
        hs = list(set(hs) - {(7, -3), (8, 11), (10, -2)} | {(7, 22), (7, 23), (8, 8)})
    for m, d in hs:
        dt = datetime.date(year, m, max(1, d))
        if d < 0:
            dt += ((7 - dt.weekday()) % 7 + 7 * (-1 - d)) * t
        if dt.weekday() == 6:
            dt += t
        while dt in res:
            dt += t
        res.append(dt)
    res = sorted(res)
    for d1, d2 in zip(res[:-1], res[1:]):
        if (d2 - d1).days == 2:
            res.append(d1 + datetime.timedelta(1))
    return set(res)


class ColorTextCalendar(clndr.TextCalendar):
    _theyear = -1
    _holiday: Set[datetime.date] = set()
    _themonth = -1

    @staticmethod
    def _set_theyear(theyear):
        ColorTextCalendar._theyear = theyear
        ColorTextCalendar._holiday = holiday(theyear)

    @staticmethod
    def _day(day):
        cls = ColorTextCalendar
        return datetime.date(cls._theyear, cls._themonth, day)

    def formatday(self, day, weekday, width):
        return (
            ""
            if day == 0
            else "\x1b[1;31m%2i\x1b[0m" % day
            if weekday == 6 or ColorTextCalendar._day(day) in ColorTextCalendar._holiday
            else "\x1b[1;36m%2i\x1b[0m" % day
            if weekday == 5
            else "%2i" % day
        ).center(width)

    def formatweekday(self, day, width):
        s = super().formatweekday(day, width)
        f1, f2 = "\x1b[1;31m%s\x1b[0m", "\x1b[1;36m%s\x1b[0m"
        return f1 % s if day == 6 else f2 % s if day == 5 else s

    def formatmonth(self, theyear, themonth, width, withyear=True):
        ColorTextCalendar._set_theyear(theyear)
        ColorTextCalendar._themonth = themonth
        return super().formatmonth(theyear, themonth, width, withyear)

    def formatyear(self, theyear, w=2, ln=1, c=6, m=3):
        ColorTextCalendar._set_theyear(theyear)
        w = max(2, w)
        ln = max(1, ln)
        c = max(2, c)
        colwidth = (w + 1) * 7 - 1
        v = []
        a = v.append
        a(repr(theyear).center(colwidth * m + c * (m - 1)).rstrip())
        a("\n" * ln)
        header = self.formatweekheader(w)
        for (i, row) in enumerate(self.yeardays2calendar(theyear, m)):
            # months in this row
            months = range(m * i + 1, min(m * (i + 1) + 1, 13))
            a("\n" * ln)
            names = (self.formatmonthname(theyear, k, colwidth, False) for k in months)
            a(clndr.formatstring(names, colwidth, c).rstrip())
            a("\n" * ln)
            headers = (header for k in months)
            a(clndr.formatstring(headers, colwidth, c).rstrip())
            a("\n" * ln)
            # max number of weeks for this row
            height = max(len(cal) for cal in row)
            for j in range(height):
                weeks = []
                for k, cal in zip(months, row):
                    if j >= len(cal):
                        weeks.append("")
                    else:
                        ColorTextCalendar._themonth = k
                        weeks.append(self.formatweek(cal[j], w))
                a(clndr.formatstring(weeks, colwidth, c).rstrip())
                a("\n" * ln)
        return "".join(v)


_c = ColorTextCalendar()
firstweekday = _c.getfirstweekday
monthcalendar = _c.monthdayscalendar
prweek = _c.prweek
week = _c.formatweek
weekheader = _c.formatweekheader
prmonth = _c.prmonth
month = _c.formatmonth
calendar = _c.formatyear
prcal = _c.pryear


def main():
    theyear = int(sys.argv[1]) if len(sys.argv) > 1 else datetime.datetime.today().year
    month = int(sys.argv[2]) if len(sys.argv) > 2 else None
    if 1 <= theyear <= 12:
        month = theyear
        theyear = datetime.datetime.today().year
    if month:
        prmonth(theyear, month)
    else:
        prcal(theyear)
