#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#

import calendar
import datetime
import sys
import time

import numpy as np
import pandas as pd


def get_month_day_range(date) -> tuple[datetime.date, datetime.date]:
    """
    For a date 'date' returns the start and end date for the month of 'date'.

    Month with 31 days:
    date = datetime.date(2011, 7, 27)
    get_month_day_range(date)
    (datetime.date(2011, 7, 1), datetime.date(2011, 7, 31))

    Month with 28 days:
    date = datetime.date(2011, 2, 15)
    get_month_day_range(date)
    (datetime.date(2011, 2, 1), datetime.date(2011, 2, 28))
    """
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    first_day: datetime.date = date.replace(day=1)
    last_day: datetime.date = date.replace(day=calendar.monthrange(date.year, date.month)[1])
    return first_day, last_day


def get_quarter(date: datetime) -> datetime:
    """
        Returns the quarter number for a given date.
    """
    return (date.month - 1) // 3 + 1


def get_first_day_of_the_quarter(date: datetime) -> datetime:
    """
    This function returns the first day of the quarter for a given date.

    :param date: A datetime object representing a date
    :type date: datetime.datetime
    :return: A datetime object representing the first day of the quarter
    :rtype: datetime.datetime
    """
    return datetime.datetime(date.year, 3 * ((date.month - 1) // 3) + 1, 1)


def get_last_day_of_the_quarter(date: datetime) -> datetime:
    """
        This function returns the last day of the quarter for a given date.

        :param date: A datetime object representing a date
        :type date: datetime.datetime
        :return: A datetime object representing the last day of the quarter
        :rtype: datetime.datetime
    """
    quarter = get_quarter(date)
    return datetime.datetime(date.year + 3 * quarter // 12, 3 * quarter % 12 + 1, 1) + datetime.timedelta(days=-1)


def get_quarter_date_range(year, quarter):
    quarter_start_month = (quarter - 1) * 3 + 1
    quarter_start = datetime.datetime(year, quarter_start_month, 1)
    quarter_end = quarter_start + datetime.timedelta(days=90)
    return quarter_start, quarter_end


def get_quarter_timerange(date):
    """
    Returns the start and end dates of a quarter for a given year and quarter number.
    """
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    start = get_day_starttime(get_first_day_of_the_quarter(date))
    end = get_day_endtime(get_last_day_of_the_quarter(date))
    return start, end


def get_day_timerange(date):
    """
        Returns the start and end times of a given date.
    """
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    start = datetime.datetime.combine(date, datetime.time.min)
    end = datetime.datetime.combine(date, datetime.time.max)
    return start, end


def get_day_starttime(date):
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    return datetime.datetime.combine(date, datetime.time.min)


def get_day_endtime(date):
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    return datetime.datetime.combine(date, datetime.time.max)


def remove_tz_from_datefield(df, date_fields):
    for date_field in date_fields:
        df[date_field] = pd.to_datetime(df[date_field], errors='coerce')
        df[date_field].fillna(pd.to_datetime(datetime.datetime.today(), format='%Y-%m-%d'), inplace=True)
        df[date_field] = df[date_field].apply(
            lambda a: datetime.datetime.strftime(a, "%Y-%m-%d %H:%M:%S"))
        df[date_field] = pd.to_datetime(df[date_field])
    return df


def calc_week_range(date):
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    current_weekday = date.weekday()
    monday = date - datetime.timedelta(days=current_weekday)
    sunday = monday + datetime.timedelta(days=6)
    return monday, sunday


def get_current_month_period():
    start, end = get_month_day_range(datetime.datetime.today())
    start = get_day_starttime(start)
    end = get_day_endtime(end)
    return start, end


def get_year_timerange(year):
    year_start = datetime.datetime.combine(
        datetime.datetime(year, 1, 1), datetime.time.min)
    year_end = datetime.datetime.combine(datetime.datetime(year, 12, 31), datetime.time.max)
    return year_start, year_end


def get_period_as_dict(start, end):
    return {
        'start': start,
        'end': end,
    }


def is_datetime_column(df, col):
    is_dt_column = False
    unique_values = df[col].unique()
    num_unique = len(unique_values)
    converted = pd.to_datetime(unique_values, errors='coerce', infer_datetime_format=True)
    num_converted = (~converted.isna()).sum()
    if num_converted / num_unique >= 0.5:
        is_dt_column = True
    return is_dt_column


def cast_col_as_datetime(df):
    for col in df.columns:
        if df[col].dtype == object:
            is_dt = is_datetime_column(df, col)
            if is_dt:
                date_format = '%Y-%m-%d %H:%M:%S'
                infer_dt = True
                if len(df[df[col].astype(str).str.contains(":") > 0]) == 0:
                    date_format = '%Y-%m-%d'
                    infer_dt = False
                df[col] = pd.to_datetime(df[col], format=date_format, errors='coerce', infer_datetime_format=infer_dt)
                df[col].fillna(method='ffill', inplace=True)
    return df


class BusinessDays:
    """
    example_holiday_list = {
        "2021": {
            "2021-01-01": "Año Nuevo",
            "2021-04-01": "Jueves Santo",
            "2021-04-02": "Viernes Santo",
            "2021-04-11": "Día de la Batalla de Rivas",
            "2021-05-03": "Dia del Trabajador",
            "2021-07-26": "Día de la Anexión del Partido de Nicoya",
            "2021-08-02": "Día de la Virgen de los Ángeles",
            "2021-08-15": "Día de la Madre",
            "2021-09-13": "Día de la Independencia",
            "2021-11-29": "Día de la abolición del ejército",
            "2021-12-25": "Navidad",
        },
    }
    """
    def __init__(self, holidays):
        self.HOLIDAY_LIST = holidays or {}
        bd_holidays = []
        for year in self.HOLIDAY_LIST:
            holidays = self.HOLIDAY_LIST[year]
            for day in holidays.keys():
                bd_holidays.append(day)
        self.bd_cal = np.busdaycalendar(holidays=bd_holidays, weekmask=[
            True, True, True, True, True, False, False])

    def get_business_days_count(self, begin_date, end_date):
        return np.busday_count(begin_date, end_date, busdaycal=self.bd_cal)


def get_current_month():
    start, end = get_current_month_period()
    return get_period_as_dict(start, end)


def get_today_timerange():
    return get_period_as_dict(get_day_starttime(datetime.datetime.today()),
                              get_day_endtime(datetime.datetime.today()))


def get_current_quarter():
    start, end = get_quarter_timerange(datetime.datetime.today())
    return get_period_as_dict(start, end)


def get_quarter_period(year, quarter):
    start, end = get_quarter_date_range(year, quarter)
    return get_period_as_dict(start, end)


def get_year_period(year):
    start, end = get_year_timerange(year)
    return get_period_as_dict(start, end)


def get_week_range(date):
    start, end = calc_week_range(date)
    return get_period_as_dict(start, end)


def count_down(msg, maximum):
    for i in range(maximum, 0, -1):
        pad_str = ' ' * len('%d' % 1)
        sys.stdout.write('%s for the next %d seconds %s\r' %
                         (msg, i, pad_str), )
        sys.stdout.flush()
        time.sleep(1)
