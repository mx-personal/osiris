import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State
import datetime as dt
from dateutil.relativedelta import relativedelta
import json
from dash import dash_table
from dash_extensions.enrich import DashProxy, MultiplexerTransform
from osiris.model.model import Model

app = DashProxy(
    __name__,
    prevent_initial_callbacks=True,
    transforms=[MultiplexerTransform()],
    external_stylesheets=[dbc.themes.COSMO]
)


# TODO Check out dbc offcanvas, dbc accordion, dbc form, navbar, spinner

app.layout = dbc.Container([
    dbc.Tabs(id='main-tabs', children=[
        dcc.Tab(id='tab-config', label='Configuration panel', children=[
            dbc.Button("Import config", id="button-import-config", color="secondary"),
            dbc.Button("Export current config", id="button-export-config", color="secondary"),
            dbc.Button("Run simulation", id="button-run-simulation", color="primary"),
            html.H5("Agent parameters"),
            dbc.Row([
                dbc.Col([html.P("Starting hunger")], width=3),
                dbc.Col(dbc.Input(id='config-hunger', type='number', placeholder="Input number"))
            ]),
            dbc.Row([
                dbc.Col([html.P("Starting energy")], width=3),
                dbc.Col(dbc.Input(id='config-energy', type='number', placeholder="Input number"))
            ]),
            dbc.Row([
                dbc.Col([html.P("Starting fun")], width=3),
                dbc.Col(dbc.Input(id='config-fun', type='number', placeholder="Input number"))
            ]),
            dbc.Row([
                dbc.Col([html.P("Reward work - Fun")], width=3),
                dbc.Col(dbc.Input(id='config-rw-work-fun', type='number', placeholder="Input number"))
            ]),
            dbc.Row([
                dbc.Col([html.P("Salary (€/year)")], width=3),
                dbc.Col(dbc.Input(id='config-salary', type='number', placeholder="Input number"))
            ]),
            dbc.Row([
                dbc.Col([html.P("Reward sleep - Energy")], width=3),
                dbc.Col(dbc.Input(id='config-rw-sleep-energy', type='number', placeholder="Input number"))
            ]),
            dbc.Row([
                dbc.Col([html.P("Parameter eat - Threshold full")], width=3),
                dbc.Col(dbc.Input(id='config-eat-thresh-full', type='number', placeholder="Input number"))
            ]),
            dbc.Row([
                dbc.Col([html.P("Parameter eat - Fill rate")], width=3),
                dbc.Col(dbc.Input(id='config-eat-fill-rate', type='number', placeholder="Input number"))
            ]),
            dbc.Row([
                dbc.Col([html.P("Parameter relax - Reward Fun")], width=3),
                dbc.Col(dbc.Input(id='config-relax-rw-fun', type='number', placeholder="Input number"))
            ]),
            dbc.Row([
                dbc.Col([html.P("Time impact - Hunger")], width=3),
                dbc.Col(dbc.Input(id='config-time-hunger', type='number', placeholder="Input number"))
            ]),
            dbc.Row([
                dbc.Col([html.P("Time impact - Energy")], width=3),
                dbc.Col(dbc.Input(id='config-time-energy', type='number', placeholder="Input number"))
            ]),
        ]),
        dcc.Tab(id='tab-results', label='Results', children=[
            dbc.Row(html.H1("Osiris"), align="start"),
            dbc.Row(html.H4("By Umbriel Draken - prototype version")),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        html.Div(id='configuration panel', children=[
                        ]),
                    ]),
                ]),
                dbc.Col([
                    dbc.DropdownMenu(label="Results", children=[
                        dbc.DropdownMenuItem("Statistics", id="menu-display-statistics"),
                        dbc.DropdownMenuItem("Graphs", id="menu-display-graphs"),
                    ]),
                    html.Div(id="container-results")
                ]),
            ]),
            dcc.Store(id="store-results"),
        ]),
    ]),
])


@app.callback(
    Output("container-results", "children"),
    Input("store-results", "data"),
    Input("menu-display-graphs", "n_clicks"),
)
def display_graphs(json_results, n_clicks_graph):
    datasets = json.loads(json_results)
    df_commod = pd.read_json(datasets["commod"], orient="split")
    fig_commod = px.line(df_commod, x='ts', y='value', color='series')
    df_actions = pd.read_json(datasets["actions"], orient="split")
    fig_actions = px.bar(df_actions, x='ts', y='value', color='series')
    return html.Div([
        dcc.Graph(figure=fig_commod),
        dcc.Graph(figure=fig_actions),
    ])


@app.callback(
    Output("container-results", "children"),
    Input("store-results", "data"),
    Input("menu-display-statistics", "n_clicks"),
)
def display_statistics(json_results, n_clicks_statistics):
    datasets = json.loads(json_results)
    results = pd.read_json(datasets["statistics"], orient="split")
    return html.Div([
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in results.columns],
            data=results.to_dict('records')
        )])


@app.callback(
    Output("store-results", "data"),
    Input("button-run-simulation", "n_clicks"),
)
def run_simulation(n_clicks):
    model = Model()
    results = model.simulate(ts_start=dt.datetime(year=2000,month=1,day=1), time_step=relativedelta(minutes=10))
    df_commod = results['commod'].copy()
    df_commod.loc[:, 'ts'] = results.loc[:, ('clock', 'ts')]
    df_commod = pd.melt(df_commod, id_vars=['ts'], value_vars=[col for col in df_commod.columns if col != 'ts'])

    df_actions = results['actions'].copy()
    df_actions.loc[:, 'ts'] = results.loc[:, ('clock', 'ts')]
    df_actions = pd.melt(df_actions, id_vars=['ts'], value_vars=[col for col in df_actions.columns if col != 'ts'])

    statistics = results.groupby(('clock', 'period - day')).sum()['actions']
    statistics['period'] = statistics.index
    statistics = statistics[[*['period'], *[col for col in statistics.columns if col != 'period']]]

    return json.dumps({
        "commod": df_commod.to_json(date_format='iso', orient='split'),
        "actions": df_actions.to_json(date_format='iso', orient='split'),
        "statistics": statistics.to_json(date_format='iso', orient='split'),
    })


from threading import Timer
import webbrowser
port = 8050


def open_browser():
    webbrowser.open_new("http://localhost:{}".format(port))

if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run_server(debug=True, port=port, usereloader=False)
