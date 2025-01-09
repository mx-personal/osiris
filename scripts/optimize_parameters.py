from scipy.optimize import differential_evolution
from src import Simulation
import datetime as dt
from dateutil import relativedelta
import os
import datetime as dt
import openpyxl
from typing import List, Dict, Literal
from globals import CONFIG_DIR, OUTPUT_DIR
import pandas as pd
from src import typical_day



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


def compute_loss(
        results: pd.DataFrame,
        include: List[str]
        ) -> Dict:
    losses = {}
    _SCHEDULE_OFF = "schedule_off"
    _SCHEDULE_WORK = "schedule_work"
    _HAPPINESS = "happiness"

    for mode in include:
        assert mode in [_HAPPINESS, _SCHEDULE_OFF, _SCHEDULE_WORK]

    if _SCHEDULE_OFF in include:
        losses[_SCHEDULE_OFF] = loss_schedule(results, "off", _TARGET_SCHEDULE['off'])
    if _SCHEDULE_WORK in include:
        losses[_SCHEDULE_WORK] = loss_schedule(results, "work", _TARGET_SCHEDULE['work'])

    return losses


def objective_function(params):
    sim = Simulation(
        clock_config = {
            "ts_start": dt.datetime(2024, 1, 1),
            "time_step_min": 15,
        },
        agent_config = {
            'eat_fill_rate': params[0],
            'eat_eff_in': params[1],
            'eat_eff_out': params[2],
            'sleep_fill_rate': params[3],
            'sleep_eff_in': params[4],
            'sleep_eff_out': params[5],
            'bored_thresh': params[6],
            'relax_fill_rate': params[7],
            'relax_eff_in': params[8],
            'relax_eff_out': params[9],
        },
    )

    sim.run()
    losses = compute_loss(
        sim.results,
        include = ['schedule_off']
        # include = ['schedule_off', "schedule_work"]
    )
    print({k: round(v, 3) for k, v in losses.items()})
    return sum(losses.values()) / len(losses)


if __name__ == "__main__":
    bounds = [
        (0, 100),   # eat fill
        (0, 1),     # eat eff in
        (0, 1),     # eat eff out
        (0, 100),   # sleep fill
        (0, 1),     # sleep eff in
        (0, 1),     # sleep eff out
        (0, 1),     # bored threshold
        (0, 100),   # relax fill rate
        (0, 1),     # relax eff in
        (0, 1),     # relax eff out
    ]

    result = differential_evolution(
        objective_function,
        bounds,
        maxiter=5,
        # tol=0.2,
    )

    optimised_param = result.x
    print(f"eat fill rate: {optimised_param[0]}")
    print(f"eat eff in: {optimised_param[1]}")
    print(f"eat eff out: {optimised_param[2]}")
    print(f"sleep fill rate: {optimised_param[3]}")
    print(f"sleep eff in: {optimised_param[4]}")
    print(f"sleep eff out: {optimised_param[5]}")

    print(f"bored thresh: {optimised_param[6]}")

    print(f"relax fill rate: {optimised_param[7]}")
    print(f"relax eff in: {optimised_param[8]}")
    print(f"relax eff out: {optimised_param[9]}")

    final_loss = objective_function(optimised_param)
    print(f"final loss: {round(100* final_loss, 2)}%")

    import yaml
    output = {
        "clock_config": {
            "ts_start": dt.datetime(2024, 1, 1),
            "time_step_min": 15,
        },
        "agent_config":{
            "eat_fill_rate": optimised_param[0],
            "eat_eff_in": optimised_param[1],
            "eat_eff_out": optimised_param[2],
            "sleep_fill_rate": optimised_param[3],
            "sleep_eff_in": optimised_param[4],
            "sleep_eff_out": optimised_param[5],
            "relax_fill_rate": optimised_param[6],
            "relax_eff_in": optimised_param[7],
            "relax_eff_out": optimised_param[8],
            "bored_thresh": optimised_param[9],
        }
    }
    # with open(OUTPUT_DIR / "sim_config_optimal.yaml") as f:
    #     yaml.dump_all()
    from src import Simulation
    sim = Simulation(**output)
    sim.run()
        

    import pdb;pdb.set_trace()
    