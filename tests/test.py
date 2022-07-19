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
import yaml
import os
import io
import base64

# Configurations
# configurations = [
#     {'title': 'Parameter 1', 'id': 'param-1', 'type': 'number', 'group': 'group-1', 'tooltip': 'yooooo'},
#     {'title': 'Parameter 2', 'id': 'param-2', 'type': 'number', 'group': 'group-1'},
#     {'title': 'Parameter 3', 'id': 'param-3', 'type': 'number', 'group': 'group-1'},
#     {'title': 'Parameter 4', 'id': 'param-4', 'type': 'number', 'group': 'group-2', 'tooltip': 'maaaate'},
#     {'title': 'Parameter 5', 'id': 'param-5', 'type': 'number', 'group': 'group-2'},
#     {'title': 'Parameter 6', 'id': 'param-6', 'type': 'number', 'group': 'group-2'},
# ]

path_internal = os.path.join(os.path.dirname(__file__))
with open(r'C:\Users\maxim\Documents\GitHub\osiris\osiris\model\parameters\visual-config.yaml','r') as f:
    _configurations = yaml.safe_load(f)

configurations = [{**{'id': k}, **v} for k, v in _configurations.items()]

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
        [
            dbc.Button("Export configuration", id='button-export-config', color='secondary'),
            # dbc.Button("Import configuration", id='button-import-config', color='secondary'),
            dcc.Upload("Import configuration", id='upload-config', className="btn-secondary", style={
                'display': 'flex',
                'height': '100%',
                'width': '100%',
                'align-items': 'center',
                'text-align': 'center',
            }),
            dbc.Button("Run simulation", id='button-run-sim', color='primary')
        ],
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
    html.Div(id='hidden-div', style={'display':'none'}),
    dcc.Download(id='download-config'),
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

# button-export-config

# @app.callback(
#     # output=[Output('hidden-div', 'children')],
#     output=[Output("download_config", "data")],
#     inputs=[Input('button-export-config', 'n_clicks')],
#     state=[State(component_id=param['id'], component_property='value') for param in configurations],
#     prevent_initial_call=True
# )
# def export_config(n_clicks, *args):
#     # print(ctx.states_list)
#     def to_yaml(bytes_io):
#         with open(bytes_io, 'w') as f:
#             yaml.dump(ctx.states_list, f)
#     return dcc.send_bytes(to_yaml, "foobar.yaml")

# from tkinter import filedialog
# @app.callback(
#     output=[Output('hidden-div', 'children')],
#     inputs=[Input('button-export-config', 'n_clicks')],
#     state=[State(component_id=param['id'], component_property='value') for param in configurations],
#     prevent_initial_call=True
# )
# def export_config(n_clicks, *args):
#     folder = filedialog.askdirectory()
#     return None


@app.callback(
    output=[Output("download-config", "data")],
    inputs=[Input('button-export-config', 'n_clicks')],
    state=[State(component_id=param['id'], component_property='value') for param in configurations],
    prevent_initial_call=True
)
def export_config(n_clicks, *args):
    dict_configs = {'agent':{config['id']: config['value'] for config in ctx.states_list if 'value' in config}}
    buffer = io.BytesIO()
    buffer.write("#configurations for agents and actions \n".encode("utf-8"))
    yaml.dump(dict_configs, buffer, encoding="utf-8")
    return dcc.send_bytes(buffer.getvalue(), "foobar.yaml")

@app.callback(
    [Output('upload-config', 'contents')] + [Output(component_id=param['id'], component_property='value') for param in configurations],
    inputs=[Input('upload-config', 'contents'), Input('upload-config', 'filename')],
    prevent_initial_call=True
)
def import_config(contents, filename):
    content_type, content = contents.split(",")
    bytes = base64.b64decode(content)
    yaml_configs = yaml.safe_load(bytes)

    # Dumping empty string in first output to empty upload button content & allow same file re-upload
    output = [''] + [yaml_configs['agent'].get(param['id'], '') for param in configurations]
    return tuple(output)

app.run_server(debug=True)
import pandas as pd
foo = pd.DataFrame()
foo.to_excel()
bar = pd.ExcelWriter

# TODO Try this structure https://towardsdatascience.com/how-to-embed-bootstrap-css-js-in-your-python-dash-app-8d95fc9e599e