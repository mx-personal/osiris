import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from osiris.model.model import Model
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State
import datetime as dt
from dateutil.relativedelta import relativedelta


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
app.layout = dbc.Container([
    dbc.Button("Run simulation", id="button-run-simulation", color="primary", className="me-1"),
    html.Div(id="results-container")
])

@app.callback(
    Output("results-container", "children"),
    Input("button-run-simulation", "n_clicks"),
)
def run_simulation(n_clicks):
    model = Model()
    results = model.simulate(ts_start=dt.datetime(year=2000,month=1,day=1), time_step=relativedelta(minutes=10))
    df_commod = results['commod'].copy()
    df_commod.loc[:, 'ts'] = results.loc[:, ('clock', 'ts')]
    df_commod = pd.melt(df_commod, id_vars=['ts'], value_vars=[col for col in df_commod.columns if col != 'ts'])
    fig_commod = px.line(df_commod, x='ts', y='value', color='series')
    return html.Div([dcc.Graph(figure=fig_commod)])


if __name__ == "__main__":
    app.run_server(debug=True)

