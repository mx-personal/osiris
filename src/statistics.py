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


def evals(results: pd.DataFrame) -> Dict:
    actions = results['actions'].columns
    analytics = pd.DataFrame(
        index=results.index,
        data={
            **{'date': results['clock']['date'],
               'period': results['clock']['duration - m'],
               'ts': results['clock']['ts'],
               'week': results['clock']['week number']
               },
            **{c: results['actions'][c] for c in actions}
        }
    )
    
    daily_analytics = analytics.groupby('date').agg({
        **{c: 'sum' for c in actions},
        **{'period': 'mean'},
        **{'week': 'first'},
    })


    for action in actions:
        daily_analytics[action] *= (daily_analytics['period'] / 60)

    weekly_analytics = daily_analytics.groupby('week').sum().drop('period', axis=1)

    output_day = pd.DataFrame(index=daily_analytics.index)
    output_day['sleep_h_ok'] = daily_analytics['sleep'] > 8

    output_week = pd.DataFrame(index=weekly_analytics.index)
    output_week['relax_h_ok'] = weekly_analytics['relax'] > 20
    output_week['clean_h_ok'] = weekly_analytics['cleanup'] > 3

    analytics_morning = analytics[(analytics['ts'].dt.hour > 5) & (analytics['ts'].dt.hour < 9)]
    analytics_night = analytics[(analytics['ts'].dt.hour < 5)].copy()
    analytics_noon = analytics[(analytics['ts'].dt.hour > 12) & (analytics['ts'].dt.hour < 14)]
    analytics_evening = analytics[(analytics['ts'].dt.hour > 18) & (analytics['ts'].dt.hour < 23)]
    analytics_night['is_sleeping'] = (analytics_night['sleep'] == 1)
    output_day['sleep_at_night'] = analytics_night.groupby('date')['is_sleeping'].all()
    output_day['eats_at_noon'] = (analytics_noon.groupby('date')['eat'].sum() >= 1)
    output_day['eats_at_eve'] = (analytics_evening.groupby('date')['eat'].sum() >= 1)
    output_day['clean_h_ok'] = (daily_analytics['cleanup'] > 15 / 60)
    output_day['washes_morning'] = (analytics_morning.groupby('date')['wash'].sum() >= 1)
    output_day['washes_eve'] = (analytics_evening.groupby('date')['wash'].sum() >= 1)
    return {
        'd_sleeps_enough': float((output_day['sleep_h_ok'] == False).sum() / len(output_day)),
        'd_sleeps_at_night': float((output_day['sleep_at_night'] == False).sum() / len(output_day)),
        'd_eats_at_noon': float((output_day['eats_at_noon'] == False).sum() / len(output_day)),
        'd_eats_at_eve': float((output_day['eats_at_eve'] == False).sum() / len(output_day)),
        'w_enough_relax': float((output_week['relax_h_ok'] == False).sum() / len(output_week)),
        'w_cleans_enough': float((output_week['clean_h_ok'] == False).sum() / len(output_week)),
        'd_washes_morning': float((output_day['washes_morning'] == False).sum() / len(output_day)),
        'd_washes_eve': float((output_day['washes_eve'] == False).sum() / len(output_day)),
    }
