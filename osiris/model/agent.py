from osiris.model import action
import datetime as dt
from dateutil import relativedelta
import yaml


class Agent (object):
    def __init__(self, name: str, sim_step: relativedelta.relativedelta, **kwargs):
        conf_commod_start = kwargs.pop("commod_start")
        conf_state_start = kwargs.pop("state_start")
        conf_actions = kwargs.pop("actions")
        conf_update_time = kwargs.pop("update_time")

        self.name = name
        self.commodities = conf_commod_start
        self.state = conf_state_start
        self.signals_int = {'drowsy': -1}
        self._log = []
        self.current_action = None

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
            action.Sleep(energy_rate=conf_actions['sleep']['energy_rate'] * hours_step),
            action.Eat(thresh_full=conf_actions['eat']['thresh_full'],
                       fill_rate=conf_actions['eat']['fill_rate'] * hours_step),
            action.Work(job="business man",
                        company="corpo ltd",
                        pay_hour=conf_actions['work']['pay'],
                        sched_work=set(sched_work),
                        rw_commod={'fun': conf_actions['work']['rw_commod']['fun'] * hours_step}),
            action.Relax(name=conf_actions['relax']['name'],
                         rw_fun=conf_actions['relax']['rw']['fun'] * hours_step,
                         effort_in=0,
                         effort_out=0)
        ]

        self.update_time = {
            'hunger': conf_update_time['hunger'] * hours_step,
            'energy': conf_update_time['energy'] * hours_step,
        }

    @classmethod
    def from_config_file(cls, name: str, sim_step: relativedelta.relativedelta, path: str):
        with open(path) as f:
            config = yaml.safe_load(f)
        # return Agent(name, sim_step, **config['agent'])
        # TODO Technical debt, find a way to better pass information from config to agent
        config = config['agent']
        return Agent(
            name,
            sim_step,
            commod_start={
                'hunger': config['start-commod-hunger'],
                'energy': config['start-commod-energy'],
                'fun': config['start-commod-fun'],
            },
            state_start=config['start-state'],
            actions={
                'work': {
                    'pay': config['work-pay'],
                    'rw_commod': {
                        'fun': config['work-rw-fun']
                    },
                },
                'sleep': {'energy_rate': config['sleep-energy-rate']},
                'eat': {
                    'thresh_full': config['eat-thres-full'],
                    'fill_rate': config['eat-fill-rate'],
                },
                'relax': {
                    'name': config['relax-name'],
                    'rw': {
                        'fun': config['relax-rw-fun']
                    },
                },
            },
            update_time={
                    'hunger':config['time-rw-hunger'],
                    'energy':config['time-rw-energy'],
            },
        )

    @property
    def current_state(self) -> {}:
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

    def update_commodities(self,update:{}):
        for stat in update:
            self.commodities[stat] = max(0,min(100, self.commodities[stat] + update[stat]))


if __name__ == "__main__":
    from pprint import pprint
    koro = Agent("koro")
    for i in range(100):
        koro.pick_action()
    [pprint(v) for v in koro.get_stats().values()]

