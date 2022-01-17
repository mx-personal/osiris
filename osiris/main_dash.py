import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
from osiris.model.model import Model
import dash_table

def run_simulation():
    model = Model()
    results = model.simulate()
    df_commod = results['commod']
    df_commod['ts'] = results['clock']['ts']
    df_commod = pd.melt(df_commod, id_vars=['ts'], value_vars=[col for col in df_commod.columns if col != 'ts'])
    fig_commod = px.line(df_commod, x='ts', y='value', color='series')

    df_actions = results['actions']
    df_actions['ts'] = results['clock']['ts']
    df_actions = pd.melt(df_actions, id_vars=['ts'], value_vars=[col for col in df_actions.columns if col != 'ts'])
    fig_actions = px.bar(df_actions, x='ts', y='value', color='series')

    statistics = results.groupby(('clock','period - day')).sum()['actions']
    statistics['period'] = statistics.index
    statistics = statistics[[*['period'], *[col for col in statistics.columns if col != 'period']]]

    return {"statistics": statistics,
            "actions": fig_actions,
            "commods": fig_commod}


results = run_simulation()
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1('Test visualisation for OSIRIS'),
    dcc.Dropdown(
        id='dropdown-graph',
        options=[
            {'label': 'graphs', 'value': 'graphs'},
            {'label': 'stats', 'value': 'stats'},
        ]
    ),
    html.Div(id='figures-container'),
])


@app.callback(
    Output('figures-container', 'children'),
    Input('dropdown-graph', 'value')
)
def update_figures(value):
    if value is None:
        return None
    elif value == "graphs":
        return html.Div([
            dcc.Graph(id='graph-actions', figure=results['actions']),
            dcc.Graph(id='graph-commods', figure=results['commods']),
        ])
    elif value == "stats":
        return html.Div([
            dash_table.DataTable(id='table',
                                 columns=[{"name": i, "id": i} for i in results['statistics'].columns],
                                 data=results['statistics'].to_dict('records'))

        ])


app.run_server(debug=True)

