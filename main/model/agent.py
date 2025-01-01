from main.model import action
import datetime as dt
from dateutil import relativedelta
from typing import Dict
from main.model.action import ActionGeneric


class Agent (object):
    current_action: ActionGeneric

    def __init__(self, name: str, sim_step: relativedelta.relativedelta):
        self.name = name
        self.commodities = {
            'hunger': 50,
            'energy': 100,
            'fun': 100 
        }
        self.signals_int = {
            'drowsy': -1,
        }
        self.state = 'awake'

        hours_working = {
            0: [(9, 13), (14, 18)],
            1: [(9, 13), (14, 18)],
            2: [(9, 13)],
            3: [(9, 13), (14, 18)],
            4: [(9, 13), (14, 18)],
            5: [],
            6: [],
        }

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
            action.Bored(),
            action.Sleep(energy_rate=10 * hours_step),
            action.Eat(thresh_full=50, fill_rate=100 * hours_step),
            action.Work(job="business man",
                        company="corpo ltd",
                        pay_hour=30000/12/4/40,
                        sched_work=set(sched_work),
                        rw_commod={'fun': -4 * hours_step}),
            action.Relax("watch tv", rw_fun=10 * hours_step, effort_in=0, effort_out=0)
        ]

        self.update_time = {
            'hunger': -4 * hours_step,
            'energy': -4 * hours_step,
        }

        self.utils = []
        self._log = []
        # self.current_action = None

    @property
    def current_state(self) -> Dict:
        data_mux = {('meta', ' state'): self.state, ('meta', 'action picked'): self.current_action}
        for dic, name in [(self.commodities, 'commod'), (self.signals_int, 'signals int')]:
            for k in dic:
                data_mux[(name, k)] = dic[k]
        data_mux[('meta', 'action picked')] = self.current_action.name
        for action in self.actions:
            data_mux[('actions', action.name)] = int(action.name == self.current_action.name)
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
        self.state = action_picked.name
        self.current_action = action_picked
        
        self.utilities = {action.name: util for action, util in zip(self.actions, utils)}

    def update_commodities(self,update:Dict):
        for stat in update:
            self.commodities[stat] = max(0,min(100, self.commodities[stat] + update[stat]))

if __name__ == "__main__":
    agent = Agent("blablou", sim_step=relativedelta.relativedelta(minutes=15))
    import pdb;pdb.set_trace()