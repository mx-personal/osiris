from src import action
import datetime as dt
from dateutil import relativedelta
from typing import Dict
from src.action import ActionGeneric


class Agent (object):
    current_action: ActionGeneric

    def __init__(
            self,
            name: str,
            sim_step: relativedelta.relativedelta,
            eat_fill_rate: float,
            eat_factor: float,
            eat_eff_in: float,
            eat_eff_out: float,
            sleep_fill_rate: float,
            sleep_factor_day: float,
            sleep_factor_night: float,
            sleep_eff_in: float,
            sleep_eff_out: float,
            bored_thresh: float,
            relax_fill_rate: float,
            relax_factor: float,
            relax_eff_in: float,
            relax_eff_out: float,
            cleanup_fill_rate: float,
            cleanup_factor: float,
            cleanup_eff_in: float,
            cleanup_eff_out: float,
        ):
        self.name = name
        self.commodities = {
            'hunger': 100,
            'energy': 100,
            'fun': 100,
            'environment': 100,
        }
        self.signals_int = {
            'drowsy': -1,
        }
        self.state = 'awake'
        self.happiness = happiness_score(self.commodities)
        hours_working = {
            0: [(9, 13), (14, 19)],
            1: [(9, 13), (14, 19)],
            2: [(9, 13), (14, 19)],
            3: [(9, 13), (14, 19)],
            4: [(9, 13), (14, 19)],
            5: [],
            6: [],
        }

        self.types_days = {k: "work" if len(v) > 0 else "off" for k, v in hours_working.items()}

        hours_step = sim_step.minutes / 60 + sim_step.hours
        ds = dt.datetime(2020, 1, 1, 0, 0, 0)
        sched_work = []
        for k in hours_working:
            for start, end in hours_working[k]:
                sched_work.extend([
                    (k, (ds + dt.timedelta(hours=start) + idx * sim_step).time())
                    for idx in range(1, int((end - start) / hours_step) + 1)
                ])
        self.actions = [
            action.Bored(threshold=bored_thresh),
            action.Sleep(
                energy_rate=sleep_fill_rate * hours_step,
                factor_day=sleep_factor_day,
                factor_night=sleep_factor_night,
                effort_in=sleep_eff_in,
                effort_out=sleep_eff_out,
            ),
            action.Eat(
                fill_rate=eat_fill_rate * hours_step,
                factor=eat_factor,
                effort_in=eat_eff_in,
                effort_out=eat_eff_out,
            ),
            action.Work(job="business man",
                        company="corpo ltd",
                        pay_hour=30000/12/4/40,
                        sched_work=set(sched_work),
                        rw_commod={'fun': -4 * hours_step}),
            action.Relax(
                "relax",
                factor=relax_factor,
                rw_fun=relax_fill_rate * hours_step,
                effort_in=relax_eff_in,
                effort_out=relax_eff_out,
            ),
            action.CleanUp(
                cleanup_fill_rate=cleanup_fill_rate,
                factor=cleanup_factor,
                effort_in=cleanup_eff_in,
                effort_out=cleanup_eff_out,
            )
        ]

        self.update_time = {
            'hunger': -4 * hours_step,
            'energy': -4 * hours_step,
            'fun': -1 * hours_step,
            'environment': -1 * hours_step, # TODO make decrease only when home
        }

        self.utils = []
        self._log = []

    @property
    def current_state(self) -> Dict:
        data_mux = {('meta', ' state'): self.state, ('meta', 'action picked'): self.current_action}
        for dic, name in [(self.commodities, 'commod'), (self.signals_int, 'signals int')]:
            for k in dic:
                data_mux[(name, k)] = dic[k]
        data_mux[('meta', 'action picked')] = self.current_action.name
        for action in self.actions:
            data_mux[('actions', action.name)] = int(action.name == self.current_action.name)
        for k, v in self.happiness.items():
            data_mux[('scores', k)] = v
        return data_mux

    def update_signals_int(self, ts):
        # Simulates serotonine secretion in circadian cycle
        h = ts.hour
        if h < 6 >= 23:  # TODO Make depend on sunset/sunrise times
            self.signals_int['drowsy'] = +1
        elif h < 21 > 9:
            self.signals_int['drowsy'] = -1
        else:
            self.signals_int['drowsy'] = 0

    def get_action(self, name):
        for action in self.actions:
            if action.name == name: return action

    def pick_action(self, ts):
        utils = [action.utility(ts, self.state, self.signals_int, self.commodities) for action in self.actions]
        action_picked = self.actions[utils.index(max(utils))]
        try:
            self.update_commodities(action_picked.rw_commod)
        except:
            import pdb;pdb.set_trace()
        self.update_commodities(self.update_time)
        self.happiness = happiness_score(self.commodities)
        self.state = action_picked.name
        self.current_action = action_picked
        self.update_signals_int(ts)
        self.utilities = {action.name: util for action, util in zip(self.actions, utils)}

    def update_commodities(self,update:Dict):
        for stat in update:
            self.commodities[stat] = max(0,min(100, self.commodities[stat] + update[stat]))

def happiness_score(commodities):
    def scoring(val):
        if val < 25:
            return 0.0
        elif val < 50:
            return 1.0
        else:
            return 2.0
    importance = {
        "hunger": 3,
        "energy": 2,
        "fun": 1,
        "environment": 1,
    }
    output = {k: scoring(commodities[k]) for k in commodities}
    output['total'] = sum([weight * score for weight, score in zip(importance.values(), output.values())]) / sum(importance.values())
    return output
