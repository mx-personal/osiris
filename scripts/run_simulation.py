from src import Simulation
import os
from pathlib import Path
from scripts.globals import CONFIG_DIR

if __name__ == "__main__":
    sim = Simulation(config=CONFIG_DIR / "sim_config.yaml")
    sim.run()
    import pdb;pdb.set_trace()
    # sim = Model(
    #     clock_config = {
    #         "ts_start": dt.datetime(2024, 1, 1),
    #         "time_step_min": 15,
    #     },
    #     agent_config = {
    #         'eat_fill_rate': 36,
    #         'eat_eff_in': 0.22,
    #         'eat_eff_out': 0.04,
    #         'sleep_fill_rate': 62,
    #         'sleep_eff_in': 0.15,
    #         'sleep_eff_out': 0.70,
    #         'bored_thresh': 0.01,
    #         'relax_fill_rate': 21.9,
    #         'relax_eff_in': 0.17,
    #         'relax_eff_out': 0.09,
    #     },
    # )
