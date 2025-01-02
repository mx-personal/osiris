from main.model.agent import Agent
from main.model.context import Clock
import main.model.context as context
import datetime as dt
from dateutil import relativedelta
import pandas as pd
from typing import Dict


_RUN = "run"
_NOT_RUN = "not run"

class Model():
    agent: Agent
    time_step: relativedelta.relativedelta

    def __init__(self):
        self.results = pd.DataFrame()
        self.status = _NOT_RUN

    def simulate(
        self,
        ts_start: dt.datetime,
        time_step: relativedelta.relativedelta,
        eat_fill_rate: float,
        eat_eff_in: float,
        eat_eff_out: float,
        sleep_fill_rate: float,
        sleep_eff_in: float,
        sleep_eff_out: float,
        bored_thresh: float,
        relax_fill_rate: float,
        relax_eff_in: float,
        relax_eff_out: float,
    ):
        self.time_step = time_step
        clock = Clock(ts_start=ts_start, time_step=time_step)
        historian = context.Historian()
        self.agent = Agent(
            "agent",
            sim_step=clock.time_step,
            eat_fill_rate=eat_fill_rate,
            eat_eff_in=eat_eff_in,
            eat_eff_out=eat_eff_out,
            sleep_fill_rate=sleep_fill_rate,
            sleep_eff_in=sleep_eff_in,
            sleep_eff_out=sleep_eff_out,
            bored_thresh=bored_thresh,
            relax_fill_rate=relax_fill_rate,
            relax_eff_in=relax_eff_in,
            relax_eff_out=relax_eff_out,
        )
        for i in range(24 * 60 * 3):
            self.agent.pick_action(clock.time)
            historian.update_log(id_agent=1, agent_state=self.agent.current_state, clock_state=clock.current_state, utilities=self.agent.utilities)
            clock.tick()
        self.results = historian.log
        self.status = _RUN

    def check_schedule(self, date: dt.date):
        if self.status != _RUN:
            print("simulation should first be run")
            exit()
        results = self.results
        commodities = results['commod'].copy()
        commodities.index = results['clock']['ts']
        output = pd.DataFrame(index = results.index)
        output['state'] = results['meta'][' state']
        output['group'] = (output['state'] != output['state'].shift()).cumsum()
        output['timestamp'] = results['clock']['ts']
        schedule = output.groupby('group').agg(
            start_idx=('state', lambda x:x.index[0]),
            end_idx=('state', lambda x:x.index[-1]),
            start_time=('timestamp', 'first'),
            end_time=('timestamp', 'last'),
            value=('state', 'first')
        )
        start = dt.datetime.combine(date, dt.datetime.min.time())
        end = start + relativedelta.relativedelta(days=1)

        return schedule[(schedule['start_time'] <= end) & (schedule['end_time'] >= start)]

    def commods(self, date: dt.date):
        results = self.results
        start = dt.datetime.combine(date, dt.datetime.min.time())
        end = start + relativedelta.relativedelta(days=1)

        daily_results =  results[(results['clock']['ts'] > start) & (results['clock']['ts'] < end)]
        output = pd.DataFrame(index = daily_results['clock']['ts'])
        for col in daily_results['commod'].columns:
            output[col] = daily_results['commod'][col].values
        return output

    def summary(self):
        # actions daily statistics
        stats = pd.DataFrame(index=self.results.index)
        stats['action_picked'] = self.results['meta']['action picked']
        stats['ts'] = self.results['clock']['ts']
        stats['day'] = stats['ts'].dt.date
        daily_actions_hours = (
            stats
            .pivot_table(index="day", columns="action_picked", aggfunc="size", fill_value=0)
            .multiply(self.time_step.minutes / 60)
        )

        daily_actions_hours['date'] = pd.to_datetime(daily_actions_hours.index)
        daily_actions_hours['weekday'] = daily_actions_hours['date'].dt.weekday
        daily_actions_hours['type_day'] = daily_actions_hours['weekday'].apply(lambda x: "working" if x<5 else "weekend")
        
        # typical day
        def get_typical_day(type_day: str) -> 'pd.DataFrame':
            daily_actions_typed = daily_actions_hours[daily_actions_hours['type_day'] == type_day].copy()
            average = daily_actions_hours[daily_actions_hours['type_day'] == type_day][[c for c in daily_actions_hours.columns if c not in ['date', 'weekday', 'type_day']]].mean()
            daily_actions_typed["diff_total"] = 0
            for idx, value in average.items():
                daily_actions_typed[f'avg_{idx}'] = value
                daily_actions_typed[f'diff2_{idx}'] = (daily_actions_typed[idx] - daily_actions_typed[f'avg_{idx}']) ** 2
                daily_actions_typed["diff_total"] += daily_actions_typed[f'diff2_{idx}']
            daily_actions_typed['diff_total'] = daily_actions_typed['diff_total'] ** (1/2)
            daily_actions_typed = daily_actions_typed.sort_values('diff_total', ascending=True)
            
            return self.check_schedule(daily_actions_typed.index[0])

        sched_typical_working = get_typical_day("working")
        sched_typical_weekend = get_typical_day("weekend")

        # scoring
        scores = self.results['commod'].copy()
        scores['ts_hour'] = self.results['clock']['ts'].dt.ceil('h')
        scores_hourly = scores.groupby('ts_hour').mean()

        def scoring(val):
            if val < 25:
                return 0
            elif val < 50:
                return 1
            else:
                return 2

        for c in scores_hourly.columns:
            scores_hourly[f'score_{c}'] = scores_hourly[c].apply(lambda x: scoring(x))

        # TODO centralise / parametrise logic
        importance = {
            "hunger": 3,
            "energy": 2,
            "fun": 1,
        }
        scores_hourly['score_total'] = 0
        for commod in importance.keys():
            scores_hourly['score_total'] += importance[commod] * scores_hourly[f'score_{commod}']

        scores_hourly['score_total'] /= sum(importance.values())

        scores_daily = scores_hourly.copy() #type: ignore
        scores_daily['ts_hour'] = pd.to_datetime(scores_hourly.index)
        scores_daily['ts_day'] = scores_daily['ts_hour'].dt.date
        scores_daily = scores_daily.drop("ts_hour", axis=1).groupby("ts_day").mean()

        scores_total: pd.DataFrame = scores_daily.mean() #type: ignore
        import os
        root = os.path.dirname(os.path.abspath(__file__))
        path_summary = os.path.join(root, 'outputs', 'results_summary.txt')
        
        with open(path_summary, 'w') as f:
            f.write(f'timestamp simulation: {dt.datetime.now()} \n')
            f.write(f"total score: {round(scores_total.loc['score_total'], 2)} \n")
            f.write("\n")
            f.write("SCORES DETAILS \n")
            for commod in importance.keys():
                f.write(f"{commod} (average / score): {round(scores_total.loc[commod], 2)}")
                f.write(f" / {round(scores_total.loc[f'score_{commod}'], 2)} \n")

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
            f.write(f"date: {sched_typical_weekend.iloc[0]['end_time'].strftime('%Y-%m-%d')} \n")
            for idx, row in sched_typical_weekend.iterrows():
                f.write(f"{period_to_string(row['start_time'], row['end_time'])}: {row['value']} \n")

            f.write("\n")
            f.write("TYPICAL WORKING DAY \n")
            f.write(f"date: {sched_typical_working.iloc[0]['end_time'].strftime('%Y-%m-%d')} \n")
            for idx, row in sched_typical_working.iterrows():
                f.write(f"{period_to_string(row['start_time'], row['end_time'])}: {row['value']} \n")

        path_details = os.path.join(root, 'outputs', 'details.csv')
        self.results.to_csv(path_details)

if __name__ == "__main__":
    # ts_start = dt.datetime(2024, 1, 1)
    # time_step = relativedelta.relativedelta(minutes=15)
    # sim = Model()
    # sim.simulate(
    #     ts_start,
    #     time_step,
    #     # eat_fill_rate=60,
    # )
    # sim.summary()
    # print(sim.agent.actions[2].rw_commod)
    # import pdb;pdb.set_trace()

    ts_start = dt.datetime(2024, 1, 1)
    time_step = relativedelta.relativedelta(minutes=15)
    sim = Model()
    sim.simulate(
        ts_start,
        time_step,
        eat_fill_rate=92,
        eat_eff_in=0.6,
        eat_eff_out=0,
        # sleep_fill_rate=64,
        sleep_fill_rate=64,
        sleep_eff_in=0.22,
        # sleep_eff_out=0.38,
        sleep_eff_out=0.2,
        bored_thresh=0.055,
        relax_fill_rate=10.3,
        relax_eff_in=0.28,
        relax_eff_out=0.10,
    )
    sim.summary()
