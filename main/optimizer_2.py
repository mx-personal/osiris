from scipy.optimize import differential_evolution
from main.model.model import Model
import datetime as dt
from dateutil import relativedelta
import os
import datetime as dt
import openpyxl
from typing import List, Dict


def get_target_actions():
    root = os.path.dirname(os.path.abspath(__file__))
    path_schedules = os.path.join(root, 'parameters', 'optimal-schedule.xlsx')
    wb = openpyxl.load_workbook(path_schedules)
    sh = wb['Sheet1']

    schedule_working = {}
    schedule_off = {}
    for idx, row in enumerate(sh.iter_rows(values_only=True)):
        if isinstance(row[0], dt.time):
            schedule_working[row[0]] = row[1]
            schedule_off[row[3]] = row[4]
        elif isinstance(row[0], dt.datetime):
            schedule_working[row[0].time()] = row[1]
            schedule_off[row[3].time()] = row[4]


    ts_start = dt.datetime(2024, 1, 1)
    sim_step = relativedelta.relativedelta(minutes=15)
    target = []
    current_time = ts_start
    for i in range(24 * 60 * 3):
        date = current_time.date()

        if date.weekday() < 5: # working day
            target.append({
                "ts": current_time,
                "action": schedule_working[current_time.time()]
            })
        else: # off day
            target.append({
                "ts": current_time,
                "action": schedule_off[current_time.time()]
            })
        
        current_time += sim_step
        target_actions = [dic['action'] for dic in target]

    return target_actions

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

# bounds = [(0, 100)]

"""
TODO remake to have criteria:
- typical work day matches 80% target schedule -> score = % match
- typical off day matches 80% target schedule -> score = % match
- happiness >= 2 -> score = happiness over 3
"""

def compute_loss(simulated_actions, target_actions):
    output = 0
    for sim_action, target_action in zip(simulated_actions, target_actions):
        if sim_action != target_action:
            output +=1
    return output / len(simulated_actions)


target_actions = get_target_actions()

# def objective_function(params):
#     sim = Model()
#     sim.simulate(
#         ts_start=dt.datetime(2024, 1, 1),
#         time_step=relativedelta.relativedelta(minutes=15),
#     )
#     return 0

# result = differential_evolution(
#     objective_function,
#     bounds
# )


def objective_function(params):
    sim = Model()
    sim.simulate(
        ts_start=dt.datetime(2024, 1, 1),
        time_step=relativedelta.relativedelta(minutes=15),
        eat_fill_rate=params[0],
        eat_eff_in=params[1],
        eat_eff_out=params[2],
        sleep_fill_rate=params[3],
        sleep_eff_in=params[4],
        sleep_eff_out=params[5],
        bored_thresh=params[6],
        relax_fill_rate=params[7],
        relax_eff_in=params[8],
        relax_eff_out=params[9],
    )
    loss = compute_loss(simulated_actions=sim.results['meta']['action picked'].values, target_actions=target_actions)
    return loss

result = differential_evolution(
    objective_function,
    bounds,
    maxiter=50,
    tol=0.2,
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
import pdb;pdb.set_trace()
