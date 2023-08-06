# from Checkbox import *
from Dropdown import *
import dash
from dash import html, Output, Input
# import os

# current_directory = os.getcwd()
# file_name = 'dbc.css'
# file_path = os.path.join(current_directory, 'assets', file_name)

# app = dash.Dash(external_stylesheets=[file_path])
app = dash.Dash(external_stylesheets=[])

app.layout = html.Div([
    # html.H1(id="input-text2", children='My Dash App'),
    html.Div(Dropdown(
        dropdown_props={
            "id": "drop-down",
            "options": [{'label': 'JAN', 'value': 'M1'},
                        {'label': 'FEB', 'value': 'M2'},
                        {'label': 'MAR', 'value': 'M3'},
                        {'label': 'APR', 'value': 'M4'},
                        {'label': 'MAY', 'value': 'M5'},
                        {'label': 'JUN', 'value': 'M6'},
                        {'label': 'JUL', 'value': 'M7'},
                        {'label': 'AUG', 'value': 'M8'},
                        {'label': 'SEP', 'value': 'M9'}
                        ],
            "value": 'M5',
            "placeholder": ''}),
        style={'position': 'relative',
               'width': 300,
               'height': 184,
               'top': 15,
               'left': 15,
               'border': '1px solid #0000C9',
               'border-radius': 5,
               'box-sizing': 'border-box',
               'font-family': 'Inter',
               'padding': 5,
               }
    ),
    html.Div(Checkbox(
        checklist_props={
            "id": "check-list",
            "value": [],
            "options": [
                {'label': 'New York City', 'value': 'New York City'},
                {'label': 'Montreal', 'value': 'Montreal'},
                {'label': 'San Francisco', 'value': 'San Francisco'}
            ],
            'inputStyle': {'marginRight': '0.5rem', 'backgroundColor': 'blue', 'borderColor': 'blue'}
                        },
                    ),
        style={'position': 'relative',
               'width': 300,
               'height': 184,
               'top': 15,
               'left': 15,
               'border': '1px solid #7B61FF',
               'border-radius': 5,
               'box-sizing': 'border-box',
               'font-family': 'Inter',
               'padding': 5,
               }
            ),
    html.H1(id="output-text", children='output to be shown')]
    )


@app.callback(Output("output-text", "children"),
              Input("check-list", "value"))
def update_output(input_value):
    return "Data you entered is : {}".format(input_value)


if __name__ == "__main__":
    app.run_server(debug=True)
