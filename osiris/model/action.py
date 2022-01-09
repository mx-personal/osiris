import datetime as dt
from osiris.model import functions as func


class ActionGeneric(object):
    def __init__(self, name: str, rw_commod: {} = None, rw_mat: {} = None, effort_in: float = 0, effort_out: float = 0):
        if rw_commod is None:
            rw_commod = {}
        if rw_mat is None:
            rw_mat = {}
        self.name = name
        self.rw_mat = rw_mat
        self.rw_commod = rw_commod
        self.effort_out = effort_out
        self.effort_in = effort_in


class Relax(ActionGeneric):
    _UTIL_INF_PRONE = func.util('inf', risk_profile='prone')

    def __init__(self, name, rw_fun, effort_in, effort_out):
        super().__init__(
            name=name,
            rw_commod={'fun': rw_fun},
            effort_in=effort_in,
            effort_out=effort_out
        )

    def utility(self, ts, state_curr, signals: {}, commodities: {}):
        if state_curr == self.name:
            bonus_state = self.effort_out
        else:
            bonus_state = - self.effort_in
        return min(1, bonus_state + self.__class__._UTIL_INF_PRONE(commodities['fun']))


class Eat(ActionGeneric):
    def __init__(self, thresh_full, fill_rate:float):
        super().__init__(
            name="eat",
            rw_commod={'hunger': +fill_rate},
            effort_in=0.1,
            effort_out=0
        )
        self.util_base = func.util('thresh', risk_profile='prone', threshold=thresh_full)

    def utility(self, ts, state_curr, signals: {}, commodities: {}):
        if state_curr == self.name:
            bonus_state = self.effort_out
        else:
            bonus_state = - self.effort_in
        return min(1, bonus_state + self.util_base(commodities['hunger']))


class Work(ActionGeneric):
    def __init__(self, job: str, company: str, pay_hour: float, sched_work: set, rw_commod):
        self.job = job
        self.company = company
        self.pay_month = pay_hour
        self.sched_work = sched_work

        super().__init__(
            name="work",
            rw_mat={'money': pay_hour},
            rw_commod=rw_commod,
            effort_in=0,
            effort_out=0
        )

    def utility(self, ts: dt.datetime, state_curr, signals: {}, commodities: {}):
        if (ts.weekday(), ts.time()) in self.sched_work:
            return 1
        else:
            return -1


class Sleep(ActionGeneric):
    _UTIL_INF_PRONE = func.util('inf', risk_profile='prone')
    _UTIL_INF_NEUTRAL = func.util('inf', risk_profile='neutral')
    _UTIL_INF_ADVERSE = func.util('inf', risk_profile='adverse')

    def __init__(self, energy_rate:float):
        super().__init__(
            name="sleep",
            rw_commod={'energy': energy_rate},
            effort_in=0.5,
            effort_out=0.7
        )

    def utility(self, ts, state_curr, signals: {}, commodities: {}):
        if state_curr == self.name:
            bonus_state = self.effort_out
        else:
            bonus_state = - self.effort_in

        if signals['drowsy'] == 1:
            util = self.__class__._UTIL_INF_PRONE
        elif signals['drowsy'] == 0:
            util = self.__class__._UTIL_INF_NEUTRAL
        else:
            util = self.__class__._UTIL_INF_ADVERSE
        return min(1, bonus_state + util(commodities['energy']))


if __name__ == "__main__":
    foo = Sleep()
    import pdb
    pdb.set_trace()