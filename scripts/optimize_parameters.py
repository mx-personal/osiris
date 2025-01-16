from scipy.optimize import differential_evolution, minimize
from src import Simulation
import datetime as dt
from dateutil import relativedelta
from run_simulation import summary
import os
import datetime as dt
import openpyxl
from typing import List, Dict, Literal, Callable
from globals import CONFIG_DIR, OUTPUT_DIR
import pandas as pd
from src import typical_day, evals
import yaml
from dataclasses import dataclass
from src import average_scores

class Parameter:
    name: str
    default: float
    lbound: float
    ubound: float
    value: float

    def __init__(self, name, default, lbound, ubound):
        self.name = name
        self.default = default
        self.lbound = lbound
        self.ubound = ubound


def get_target_actions():
    wb = openpyxl.load_workbook(CONFIG_DIR / 'optimal-schedule.xlsx')
    sh = wb['Sheet1']

    schedule_work = []
    schedule_off = []
    
    def build_row(idx, val):
        return {
            "ts": idx,
            "val": val
        }

    for idx, row in enumerate(sh.iter_rows(values_only=True)):
        if isinstance(row[0], dt.time):
            schedule_work.append(build_row(row[0], row[1]))
        elif isinstance(row[0], dt.datetime):
            schedule_work.append(build_row(row[0].time(), row[1]))

        if isinstance(row[3], dt.time):
            schedule_off.append(build_row(row[3], row[4]))
        elif isinstance(row[3], dt.datetime):
            schedule_off.append(build_row(row[3].time(), row[4]))
    return {
        "work": pd.DataFrame.from_records(schedule_work),
        "off": pd.DataFrame.from_records(schedule_off),
    }

_TARGET_SCHEDULE = get_target_actions()

def loss_schedule(
        results: pd.DataFrame,
        type_day: Literal["work", "off"],
        target_schedule: pd.DataFrame
        ) -> float:
    typical_day_actual = typical_day(results, type_day=type_day)    
    count_mismatch = 0
    count_values = 0
    for val, target in zip(typical_day_actual['meta']['action picked'].values, target_schedule['val'].values):
        if target != 'any':
            count_values += 1
            if val != target:
                count_mismatch += 1
    return count_mismatch / count_values


def loss_averages(results: pd.DataFrame) -> float:
    import pdb;pdb.set_trace()
    return 0.0

def loss_happiness(results: pd.DataFrame) -> float:
    return 1 - float(results['scores'].mean().mean()) / 3 # type: ignore


def compute_loss(
        results: pd.DataFrame,
        include: List[str]
        ) -> Dict:
    losses = {}
    _SCHEDULE_OFF = "schedule_off"
    _SCHEDULE_WORK = "schedule_work"
    _HAPPINESS = "happiness"
    _AVERAGES = "average"
    _GOOD_HABITS = 'habits'
    

    for mode in include:
        assert mode in [_HAPPINESS, _SCHEDULE_OFF, _SCHEDULE_WORK, _AVERAGES, _GOOD_HABITS]

    if _SCHEDULE_OFF in include:
        losses[_SCHEDULE_OFF] = loss_schedule(results, "off", _TARGET_SCHEDULE['off'])
    if _SCHEDULE_WORK in include:
        losses[_SCHEDULE_WORK] = loss_schedule(results, "work", _TARGET_SCHEDULE['work'])
    if _AVERAGES in include:
        losses[_AVERAGES] = loss_averages(results)
    if _HAPPINESS in include:
        losses[_HAPPINESS] = loss_happiness(results)
    if _GOOD_HABITS in include:
        loss_habits = evals(results)
        # output_str = ",".join([f'{k}:' + '{:.3f}'.format(v) for k,v in losses.items()])
        # print(output_str)
        losses[_GOOD_HABITS] = sum(loss_habits.values()) / len(loss_habits.values())

    return losses


def objective_function(parameters: List[Parameter], include: List[str]) -> Callable[[List[float]], float]:

    def _objective_function(params):
        sim = Simulation(
            clock = {
                "ts_start": dt.datetime(2024, 1, 1),
                "time_step_min": 15,
            },
            agent = {param.name: params[idx] for idx, param in enumerate(parameters)},
        )
        sim.run()
        losses = compute_loss(
            sim.results,
            include=include,
        )
        # print({k: round(v, 3) for k, v in losses.items()})
        return sum(losses.values()) / len(losses)

    return _objective_function

def params_to_config(params: List[Parameter]) -> Dict:
    return {
        "clock": {
            "ts_start": dt.datetime(2024, 1, 1),
            "time_step_min": 15,
        },
        "agent":{param.name: param.value for param in params}
    }

def save_results(parameters: List[Parameter], file_name: str):
    configs = params_to_config(parameters)
    with open(OUTPUT_DIR / f"{file_name}.yaml", "w") as f:
        yaml.dump(configs, f)

_LBOUND_EFF = 0
_UBOUND_EFF = 1
_LBOUND_FACTOR = 0.5
_UBOUND_FACTOR = 2
_LBOUND_FILL = 0
_UBOUND_FILL = 100
#  nanme | default | lower bound | upper bound
sim_params = [
    Parameter(name='eat_fill_rate', default=50, lbound=_LBOUND_FILL, ubound=_UBOUND_FILL),
    Parameter(name='eat_factor', default=1, lbound=_LBOUND_FACTOR, ubound=_UBOUND_FACTOR),
    Parameter(name='eat_eff_in', default=1, lbound=_LBOUND_EFF, ubound=_UBOUND_EFF),
    Parameter(name='eat_eff_out', default=1, lbound=_LBOUND_EFF, ubound=_UBOUND_EFF),

    Parameter(name='sleep_fill_rate', default=50, lbound=_LBOUND_FILL, ubound=_UBOUND_FILL),
    Parameter(name='sleep_factor_day', default=1, lbound=_LBOUND_FACTOR, ubound=_UBOUND_FACTOR),
    Parameter(name='sleep_factor_night', default=1, lbound=_LBOUND_FACTOR, ubound=_UBOUND_FACTOR),
    Parameter(name='sleep_eff_in', default=1, lbound=_LBOUND_EFF, ubound=_UBOUND_EFF),
    Parameter(name='sleep_eff_out', default=1, lbound=_LBOUND_EFF, ubound=_UBOUND_EFF),

    Parameter(name='relax_fill_rate', default=50, lbound=_LBOUND_FILL, ubound=_UBOUND_FILL),
    Parameter(name='relax_factor', default=1, lbound=_LBOUND_FACTOR, ubound=_UBOUND_FACTOR),
    Parameter(name='relax_eff_in', default=1, lbound=_LBOUND_EFF, ubound=_UBOUND_EFF),
    Parameter(name='relax_eff_out', default=1, lbound=_LBOUND_EFF, ubound=_UBOUND_EFF),

    Parameter(name='cleanup_fill_rate', default=50, lbound=_LBOUND_FILL, ubound=_UBOUND_FILL),
    Parameter(name='cleanup_factor', default=1, lbound=_LBOUND_FACTOR, ubound=_UBOUND_FACTOR),
    Parameter(name='cleanup_eff_in', default=1, lbound=_LBOUND_EFF, ubound=_UBOUND_EFF),
    Parameter(name='cleanup_eff_out', default=1, lbound=_LBOUND_EFF, ubound=_UBOUND_EFF),

    Parameter(name='bored_thresh', default=0.20, lbound=_LBOUND_EFF, ubound=_UBOUND_EFF),

]

if __name__ == "__main__":
    from src import Simulation

    bounds = [(param.lbound, param.ubound) for param in sim_params]
    # includes = [['schedule_off', 'schedule_work']]
    # includes = [['schedule_work', 'schedule_off', 'happiness']]
    # includes = [['schedule_work', 'happiness']]
    includes = [['habits']]
    results = []
    for include in includes:
        print(f"running simulation for {include}")
        func = objective_function(sim_params, include=include)
        for id_agent in range(5):
            print(f"running optim for agent {id_agent}")
            result = differential_evolution(
                func,
                bounds,
                # maxiter=1,
                tol=0.2,
            )
            for idx, param in enumerate(sim_params):
                param.value = float(result.x[idx])
            configs = params_to_config(sim_params)
            save_results(sim_params, f'optimised-{id_agent}')

            sim = Simulation(**configs)
            sim.run()

            results.append(
                {
                    'agent_id': id_agent,
                    'file': f'optimised-{id_agent}',
                    'score_total': average_scores(sim.results)['total'],
                    'commodities': average_scores(sim.results)['commodities'],
                }
            )
        from pprint import pprint
        pprint(results)
        import pdb;pdb.set_trace()

        sim = Simulation(**configs)
        sim.run()
        
        loss = compute_loss(sim.results, include=['schedule_work', 'schedule_off', 'happiness'])
        print("---- Final results ----")
        print(f"Score schedule work: {loss['schedule_work']}")
        print(f"Score schedule off: {loss['schedule_off']}")
        print(f"Score happiness: {loss['happiness']}")

        summary(sim)
        import pdb;pdb.set_trace()
    