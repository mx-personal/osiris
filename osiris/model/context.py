import datetime as dt
from dateutil.relativedelta import relativedelta
import pandas as pd

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
    def __init__(self):
        self.t0 = dt.datetime(2000, 1, 1, 0, 0, 0)
        self.time = self.t0
        self.time_step = relativedelta(minutes=10)
        self.period_day = self.get_period_day()
        self.period_week = self.get_period_week()
        self.period_year = self.get_period_year()

    def tick(self):
        self.time += self.time_step

    @property
    def current_state(self):
        return {
            'ts': self.time,
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


    # TODO DRY
    def get_period_year(self) -> str:
        for title, periods in _PERIODS_YEAR.items():
            for ms, me in periods:
                if ms <= self.time.month < me:
                    return title

    def get_period_week(self) -> str:
        return _PERIODS_WEEK[self.time.weekday()]


class Historian(object):
    def __init__(self):
        self._logs = []

    def update_log(self, id_agent: int, agent_state: {}, clock_state: {}):
        self._logs.append({
            ('meta', 'id_agent'): id_agent,
            **agent_state,
            **{('clock', k): v for k, v in clock_state.items()}
        })

    @property
    def log(self):
        return pd.DataFrame(
            data=self._logs,
            columns=pd.MultiIndex.from_tuples(tuples=self._logs[0].keys(), names=['category','series']),
        )

