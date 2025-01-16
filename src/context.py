import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd
from typing import Dict
from src.agent import Agent

_PERIODS_DAY = {
    'NIGHT': [(0, 6), (19, 24)],
    'SUNRISE': [(6, 8)],
    'MORNING': [(8, 12)],
    'NOON': [(12, 14)],
    'AFTERNOON': [(14, 17)],
    'SUNSET': [(17, 19)],
}

_PERIODS_WEEK = {
    0: "MONDAY",
    1: "TUESDAY",
    2: "WEDNESDAY",
    3: "THURSDAY",
    4: "FRIDAY",
    5: "SATURDAY",
    6: "SUNDAY",
}

_PERIODS_YEAR = {
    "SPRING": [(3, 6)],
    "SUMMER": [(6, 9)],
    "FALL": [(9, 11)],
    "WINTER": [(12, 13), (1, 3)],
}


class Clock(object):
    def __init__(self, ts_start: dt.datetime, time_step_min: int):
        self.t0 = ts_start
        self.time = self.t0
        self.time_step = relativedelta(minutes=time_step_min)
        self.period_day = self.get_period_day()
        self.period_week = self.get_period_week()
        self.period_year = self.get_period_year()

    def tick(self):
        self.time += self.time_step
        self.period_day = self.get_period_day()
        self.period_week = self.get_period_week()
        self.period_year = self.get_period_year()

    @property
    def current_state(self):
        def round_to_hour(dt: dt.datetime) -> dt.datetime:
            if dt.minute > 0:
                return (dt.replace(minute=0) + relativedelta(hours=1))
            return dt

        return {
            'ts': self.time,
            'ts - time': self.time.time(),
            'ts - hour': round_to_hour(self.time),
            'duration - m': self.time_step.minutes,
            'week number': self.time.isocalendar().week,
            'date': self.time.date(),
            'period - day': self.period_day,
            'period - week': self.period_week,
            'period - year': self.period_year,
        }

    # TODO DRY
    def get_period_day(self) -> str:
        tst = self.time.time()
        for title, periods in _PERIODS_DAY.items():
            for hs, he in periods:
                if hs <= tst.hour < he:
                    return title
        raise Exception

    # TODO DRY
    def get_period_year(self) -> str:
        for title, periods in _PERIODS_YEAR.items():
            for ms, me in periods:
                if ms <= self.time.month < me:
                    return title
        raise Exception

    def get_period_week(self) -> str:
        return _PERIODS_WEEK[self.time.weekday()]


class Historian(object):
    def __init__(self):
        self._logs = []

    def update_log(self, agent: Agent, clock: Clock):
        self._logs.append({
            **agent.current_state,
            **{('clock', k): v for k, v in clock.current_state.items()},
            ('clock', 'type_day'): agent.types_days[clock.current_state['ts'].weekday()],
            **{('utils', k): v for k, v in agent.utilities.items()},
        })

    @property
    def log(self):
        return pd.DataFrame(
            data=self._logs,
            columns=pd.MultiIndex.from_tuples(tuples=self._logs[0].keys(), names=['category','series']),
        )
