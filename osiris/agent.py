import pandas as pd
import action
from plotly import express as px
import datetime as dt
from dateutil import relativedelta


class Agent (object):
    def __init__(self, name: str, sim_step:relativedelta.relativedelta):
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
            action.Sleep(energy_rate=10 * hours_step),
            action.Eat(thresh_full=50, fill_rate=40 * hours_step),
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

        self._log = []

    @property
    def log(self):
        return pd.DataFrame(
            data=self._log,
            columns=pd.MultiIndex.from_tuples(tuples=self._log[0].keys(), names=['category','series']),
        )

    def _update_log(self, ts, action_picked, actions):
        data_mux = {('meta', 'ts'): ts, ('meta',' state'):self.state, ('meta', 'action picked'): action_picked}
        for dic, name in [(self.commodities, 'commod'), (self.signals_int, 'signals int')]:
            for k in dic:
                data_mux[(name, k)] = dic[k]
        data_mux[('meta', 'action picked')] = action_picked.name
        for action in actions:
            data_mux[('actions', action.name)] = int(action.name == action_picked.name)
        self._log.append(data_mux)

    def display_results(self):
        df_commod = self.log['commod']
        df_commod['ts'] = self.log['meta']['ts']
        df_commod = pd.melt(df_commod, id_vars=['ts'], value_vars=[col for col in df_commod.columns if col != 'ts'])
        fig_commod = px.line(df_commod, x='ts', y='value', color='series')

        df_actions = self.log['actions']
        df_actions['ts'] = self.log['meta']['ts']
        df_actions = pd.melt(df_actions, id_vars=['ts'], value_vars=[col for col in df_actions.columns if col != 'ts'])
        fig_actions = px.bar(df_actions, x='ts', y='value', color='series')

        fig_commod.show()
        fig_actions.show()

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

    def pick_action(self,ts):
        utils = [action.utility(ts,self.state,self.signals_int,self.commodities) for action in self.actions]
        action_picked = self.actions[utils.index(max(utils))]
        try:
            self.update_commodities(action_picked.rw_commod)
        except:
            import pdb;pdb.set_trace()
        self.update_commodities(self.update_time)
        self.state = action_picked.name
        self._update_log(ts=ts,action_picked=action_picked,actions=self.actions)

    def update_commodities(self,update:{}):
        for stat in update:
            self.commodities[stat] = max(0,min(100, self.commodities[stat] + update[stat]))


if __name__ == "__main__":
    from pprint import pprint
    koro = Agent("koro")
    for i in range(100):
        koro.pick_action()
    [pprint(v) for v in koro.get_stats().values()]

