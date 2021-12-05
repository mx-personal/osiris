import datetime as dt
from dateutil.relativedelta import relativedelta


class Clock(object):
    def __init__(self):
        self.t0 = dt.datetime(2000,1,1,0,0,0)
        self.time = self.t0
        self.time_step = relativedelta(minutes=10)

    def tick(self):
        self.time += self.time_step


if __name__ == "__main__":
    foo = Clock()
