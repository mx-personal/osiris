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
from dash.exceptions import PreventUpdate
from dash import callback_context as ctx

# Configurations
configurations = [
    {'title': 'Parameter 1', 'id': 'param-1', 'type': 'number', 'group': 'group-1', 'tooltip': 'yooooo'},
    {'title': 'Parameter 2', 'id': 'param-2', 'type': 'number', 'group': 'group-1'},
    {'title': 'Parameter 3', 'id': 'param-3', 'type': 'number', 'group': 'group-1'},
    {'title': 'Parameter 4', 'id': 'param-4', 'type': 'number', 'group': 'group-2', 'tooltip': 'maaaate'},
    {'title': 'Parameter 5', 'id': 'param-5', 'type': 'number', 'group': 'group-2'},
    {'title': 'Parameter 6', 'id': 'param-6', 'type': 'number', 'group': 'group-2'},
]

_unique_groups = list(set([config['group'] for config in configurations]))
_configs = [
    {
        'group': group,
        'items': [{k: v for k, v in item.items() if k != 'group'} for item in configurations if item['group'] == group]
    }
    for group in _unique_groups
]


# App definition
def gen_param_row(name: str, id: str, type: str, tooltip: str = None):
    if tooltip is not None:
        return dbc.Row([
            dbc.Col([
                html.P(html.Span(name, id='tt-target-{0}'.format(id), style={"textDecoration": "underline", "cursor": "pointer"})),
                dbc.Tooltip(tooltip, target='tt-target-{0}'.format(id), placement='top')
            ], width=7),
            dbc.Col(dbc.Input(id, type=type))
        ])
    else:
        return dbc.Row([
            dbc.Col([html.P(name)], width=7),
            dbc.Col(dbc.Input(id, type=type))
        ])


app = DashProxy(
    __name__,
    prevent_initial_callbacks=True,
    transforms=[MultiplexerTransform()],
    external_stylesheets=[dbc.themes.COSMO]
)


template_offcanvas = html.Div([
    dbc.ButtonGroup(
        [dbc.Button("Export configuration", id='button-export-config', color='secondary'),
        dbc.Button("Import configuration", id='button-import-config', color='secondary'),
        dbc.Button("Run simulation", id='button-run-sim', color='primary')],
    ),
    dbc.Accordion([
        dbc.AccordionItem(
            [gen_param_row(name=item['title'], id=item['id'], type=item['type'], tooltip=item.get('tooltip', None)) for
             item in elt['items']],
            title=elt['group']) for elt in _configs],
        start_collapsed=True,
    ),
    html.Div(id='output-display')
])


app.layout = dbc.Container([
    dbc.Button('Configure & run', id='open-offcanvas', n_clicks=0),
    dbc.Offcanvas(template_offcanvas, id='offcanvas', title='Configurations', is_open=False)
])


@app.callback(
    Output('offcanvas', 'is_open'),
    Input('open-offcanvas', 'n_clicks'),
    [State('offcanvas', 'is_open')]
)
def toffle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


# @app.callback(
#     output=[Output('output-display', 'children')],
#     inputs=[Input(component_id=param['id'], component_property='value') for param in configurations],
#     state=[State('button-run-sim', 'n_clicks')],
# )
@app.callback(
    output=[Output('output-display', 'children')],
    inputs=[Input('button-run-sim', 'n_clicks')],
    state=[State(component_id=param['id'], component_property='value') for param in configurations],
)
def get_config(n_clicks, *args):
    return html.Plaintext("\n".join(['{0}: {1}'.format(item['id'], item.get('value', 'not set')) for item in ctx.states_list]))


app.run_server(debug=True)
