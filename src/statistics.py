import pandas as pd
from typing import Literal
from typing import Dict


def activities_summary(results: pd.DataFrame):
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
    return schedule

def typical_day(results:pd.DataFrame, type_day: Literal['work', 'off'] ) -> 'pd.DataFrame':
    stats = pd.DataFrame(index=results.index)
    stats['action_picked'] = results['meta']['action picked']
    stats['ts'] = results['clock']['ts']
    stats['date'] = results['clock']['date']
    stats['type_day'] = results['clock']['type_day']
    daily_actions_hours = (
        stats
        .pivot_table(index="date", columns="action_picked", aggfunc="size", fill_value=0)
        # .multiply(clock.time_step.minutes / 60)
    )
    daily_actions_hours['type_day'] = stats.groupby('date').first()['type_day']

    daily_actions_typed = daily_actions_hours[daily_actions_hours['type_day'] == type_day].copy()
    average = daily_actions_hours[daily_actions_hours['type_day'] == type_day][[c for c in daily_actions_hours.columns if c not in ['date', 'weekday', 'type_day']]].mean()
    daily_actions_typed["diff_total"] = 0
    for idx, value in average.items():
        daily_actions_typed[f'avg_{idx}'] = value
        daily_actions_typed[f'diff2_{idx}'] = (daily_actions_typed[idx] - daily_actions_typed[f'avg_{idx}']) ** 2
        daily_actions_typed["diff_total"] += daily_actions_typed[f'diff2_{idx}']
    daily_actions_typed['diff_total'] = daily_actions_typed['diff_total'] ** (1/2)
    daily_actions_typed = daily_actions_typed.sort_values('diff_total', ascending=True)
    date_typical = daily_actions_typed.index[0]
    return results[results['clock']['date'] == date_typical]

def average_scores(results: pd.DataFrame) -> Dict:
    """
    {
        commod: [
            {name: hunger, avg_commod: 80, score: 2}
            {name: energy, avg_commod: 80, score: 2}
            {name: fun, avg_commod: 80, score: 2}
        ]
        total: 2
    }
    """
    mean_commods = results['commod'].mean().to_dict() # type: ignore
    mean_scores = results['scores'].mean().to_dict() # type: ignore
    output = {
        'commodities': []
    }
    for k in mean_commods.keys():
        output['commodities'].append({
            "name": k,
            'average': round(mean_commods[k], 2),
            'score': round(mean_scores[k], 2),
        })
    output['total'] = mean_scores['total']
    return output

