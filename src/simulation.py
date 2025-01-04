from src.agent import Agent
from src.context import Clock
import src.context as context
import datetime as dt
from dateutil import relativedelta
import pandas as pd
from typing import Dict
import yaml

_RUN = "run"
_NOT_RUN = "not run"

class Simulation():
    def __init__(self, config=None, **kwargs):
        if config:
            with open(config) as f:
                config_args = yaml.safe_load(f)
        else:
            config_args = {}

        args_clock = {**config_args.get('clock', {}), **kwargs.get('clock_config', {})}
        
        args_agent = {**config_args.get('agent', {}), **kwargs.get('agent_config', {})}
        args_agent["sim_step"] = relativedelta.relativedelta(minutes=args_clock['time_step_min'])
        self.agent = Agent("agent", **args_agent)
        self.clock = Clock(**args_clock)

        self.historian = context.Historian()
        self.results = pd.DataFrame()
        self.status = _NOT_RUN

    def run(self):
        for i in range(24 * 30 * 3):
            self.agent.pick_action(self.clock.time)
            self.historian.update_log(
                agent=self.agent,
                clock=self.clock,
            )
            self.clock.tick()
        self.results = self.historian.log
        self.status = _RUN

    def commods(self, date: dt.date):
        results = self.results
        start = dt.datetime.combine(date, dt.datetime.min.time())
        end = start + relativedelta.relativedelta(days=1)

        daily_results =  results[(results['clock']['ts'] > start) & (results['clock']['ts'] < end)]
        output = pd.DataFrame(index = daily_results['clock']['ts'])
        for col in daily_results['commod'].columns:
            output[col] = daily_results['commod'][col].values
        return output

    def is_run(self) -> bool:
        return self.status == _RUN
