import datetime as dt
from scripts.globals import CONFIG_DIR, OUTPUT_DIR
from src import (
    Simulation,
    activities_summary,
    typical_day,
    average_scores
)

def summary(simulation: Simulation):
    results = simulation.results

    sched_typical_working = activities_summary(typical_day(results, type_day="work"))
    sched_typical_off = activities_summary(typical_day(results, type_day="off"))
    score_outputs = average_scores(results)
    
    with open(OUTPUT_DIR / "summary.txt", 'w') as f:
        f.write(f'timestamp simulation: {dt.datetime.now()} \n')
        f.write(f"total score: {score_outputs['total']} \n")

        f.write("\n")
        f.write("SCORES DETAILS \n")
        for commod in score_outputs['commodities']:
            f.write(f"{commod['name']} (average / score): {commod['average']} / {commod['score']}\n")

        f.write("\n")

        def period_to_string(start: dt.datetime, end: dt.datetime) -> str:
            period = f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"
            duration = time_diff_to_string(start, end)
            return f"{period} ({duration})"

        def time_diff_to_string(start: dt.datetime, end: dt.datetime) -> str:
            diff = end - start
            hours = diff.total_seconds() // 3600
            minutes = (diff.total_seconds() % 3600) // 60
            return f"{round(int(hours))}h{int(minutes)}m"

        f.write("TYPICAL OFF DAY \n")
        f.write(f"date: {sched_typical_off.iloc[0]['end_time'].strftime('%Y-%m-%d')} \n")
        for idx, row in sched_typical_off.iterrows():
            f.write(f"{period_to_string(row['start_time'], row['end_time'])}: {row['value']} \n")

        f.write("\n")
        f.write("TYPICAL WORKING DAY \n")
        f.write(f"date: {sched_typical_working.iloc[0]['end_time'].strftime('%Y-%m-%d')} \n")
        for idx, row in sched_typical_working.iterrows():
            f.write(f"{period_to_string(row['start_time'], row['end_time'])}: {row['value']} \n")

    results.to_csv(OUTPUT_DIR / "details.csv")



if __name__ == "__main__":
    simulation = Simulation(config=CONFIG_DIR / "sim_config.yaml")
    simulation.run()
    summary(simulation)
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
