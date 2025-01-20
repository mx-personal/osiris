import datetime as dt
from src import functions as func
from typing import Dict, Callable


class ActionGeneric(object):
    def __init__(
            self,
            name: str,
            utility: Callable,
            rw_commod: Dict = {},
            rw_mat: Dict = {},
            effort_in: float = 0,
            effort_out: float = 0,
        ):
        if rw_commod is None:
            rw_commod = {}
        if rw_mat is None:
            rw_mat = {}
        self.name = name
        self.rw_mat = rw_mat
        self.rw_commod = rw_commod
        self.effort_out = effort_out
        self.effort_in = effort_in
        self.utility = utility


class Bored(ActionGeneric):
    def __init__(self, threshold: float):
        def utility(ts, state_curr, signals: Dict, commodities: Dict):
            return self.threshold

        super().__init__(
            name="bored",
            utility=utility,
            rw_commod={},
            effort_in=0,
            effort_out=0,
        )
        self.threshold = threshold
    

class Relax(ActionGeneric):
    def __init__(self, name, rw_fun, effort_in, effort_out, factor: float):
        self.factor = factor
        base_utility = func._util_inf_free(factor)
        
        def utility(ts, state_curr, signals: Dict, commodities: Dict):
            if state_curr == self.name:
                bonus_state = self.effort_out
            else:
                bonus_state = - self.effort_in
            return min(1, bonus_state + base_utility(commodities['fun']))
        
        super().__init__(
            name=name,
            utility=utility,
            rw_commod={'fun': rw_fun},
            effort_in=effort_in,
            effort_out=effort_out
        )


class Eat(ActionGeneric):
    def __init__(self, fill_rate:float, effort_in: float, effort_out: float, factor: float):
        self.factor = factor
        base_utility = func._util_inf_free(factor)
        def utility(ts, state_curr, signals: Dict, commodities: Dict):
            if state_curr == self.name:
                bonus_state = self.effort_out
            else:
                bonus_state = - self.effort_in
            return min(1, bonus_state + base_utility(commodities['hunger']))
        
        super().__init__(
            name="eat",
            utility=utility,
            rw_commod={'hunger': + fill_rate},
            effort_in=effort_in,
            effort_out=effort_out,
        )


class Work(ActionGeneric):
    def __init__(self, job: str, company: str, pay_hour: float, sched_work: set, rw_commod):
        def utility(ts: dt.datetime, state_curr, signals: Dict, commodities: Dict):
            if (ts.weekday(), ts.time()) in self.sched_work:
                return 1
            else:
                return -1

        self.job = job
        self.company = company
        self.pay_month = pay_hour
        self.sched_work = sched_work

        super().__init__(
            name="work",
            utility=utility,
            rw_mat={'money': pay_hour},
            rw_commod=rw_commod,
            effort_in=0,
            effort_out=0
        )


class Sleep(ActionGeneric):
    def __init__(self, energy_rate:float, effort_in: float, effort_out: float, factor_day: float, factor_night: float):
        self.factor_day = factor_day
        self.factor_night = factor_night
        utility_day = func._util_inf_free(factor_day)
        utility_night = func._util_inf_free(factor_night)

        def utility(ts, state_curr, signals: Dict, commodities: Dict):
            if state_curr == self.name:
                bonus_state = self.effort_out
            else:
                bonus_state = - self.effort_in

            if signals['drowsy'] == 1:
                util = utility_night
            elif signals['drowsy'] == 0:
                util = utility_day
            else:
                util = utility_day
            return max(0, min(1, bonus_state + util(commodities['energy'])))

        super().__init__(
            name="sleep",
            utility=utility,
            rw_commod={'energy': energy_rate},
            effort_in=effort_in,
            effort_out=effort_out,
        )

class CleanUp(ActionGeneric):
    def __init__(self, cleanup_fill_rate:float, effort_in: float, effort_out: float, factor: float):
        self.factor = factor
        base_utility = func._util_inf_free(factor)

        def utility(ts, state_curr, signals: Dict, commodities: Dict):
            if state_curr == self.name:
                bonus_state = self.effort_out
            else:
                bonus_state = - self.effort_in
            return min(1, bonus_state + base_utility(commodities['hygiene_env']))

        super().__init__(
            name="cleanup",
            utility=utility,
            rw_commod={'hygiene_env': cleanup_fill_rate},
            effort_in=effort_in,
            effort_out=effort_out,
        )


class Wash(ActionGeneric):
    def __init__(self, fill_rate:float, effort_in: float, effort_out: float, factor: float):
        self.factor = factor
        base_utility = func._util_inf_free(factor)

        def utility(ts, state_curr, signals: Dict, commodities: Dict):
            if state_curr == self.name:
                bonus_state = self.effort_out
            else:
                bonus_state = - self.effort_in
            return min(1, bonus_state + base_utility(commodities['hygiene_self']))

        super().__init__(
            name="wash",
            utility=utility,
            rw_commod={'hygiene_self': fill_rate},
            effort_in=effort_in,
            effort_out=effort_out,
        )
