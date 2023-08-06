from dash import html, dcc
import dash
import os

current_directory = os.getcwd()
file_name = 'dbc.css'
file_path = os.path.join(current_directory, 'assets', file_name)

app = dash.Dash(external_stylesheets=[file_path])

app.layout = html.Div([
    html.Div(
        [
            # html.H3(className='label', children="Label"),
            dcc.Dropdown(
                options=[{'label': 'JAN', 'value': 'M1'},
                         {'label': 'FEB', 'value': 'M2'},
                         {'label': 'MAR', 'value': 'M3'},
                         {'label': 'APR', 'value': 'M4'},
                         {'label': 'MAY', 'value': 'M5'},
                         {'label': 'JUN', 'value': 'M6'},
                         {'label': 'JUL', 'value': 'M7'},
                         {'label': 'AUG', 'value': 'M8'},
                         {'label': 'SEP', 'value': 'M9'}
                         ],
                value='M5',
                placeholder='',
                        )
        ],
        style={'position': 'relative',
               'width': 525,
               'height': 282,
               'top': 100,
               'left': 400,
               'border': '1px dashed #7B61FF',
               'border-radius': 5,
               'box-sizing': 'border-box',
               }
    ),
    html.Div(className='dbc-row-selectable',
             children=[
                 html.H3(className='label', children="Label",
                         ),
                 dcc.Checklist(
                     options=[{'label': html.Span("January", className='checkboxfont'), 'value': 'M1', },
                              {'label': html.Span("Feb", className='checkboxfont'), 'value': 'M2'},
                              {'label': html.Span("Mar", className='checkboxfont'), 'value': 'M3'},
                              {'label': html.Span("Apr", className='checkboxfont'), 'value': 'M4'},
                              {'label': html.Span("May", className='checkboxfont'), 'value': 'M5'}],
                     value=['M2', 'M3', 'M5']
                 )
             ],
             style={'position': 'relative',
                    'width': 300,
                    'height': 184,
                    'top': -122,
                    'left': 54,
                    'border': '1px solid #7B61FF',
                    'border-radius': 5,
                    'box-sizing': 'border-box',
                    'font-family': 'Inter',
                    }
             )], style={'backgroundColor': '#EAEAEA', 'margin': 0})
if __name__ == '__main__':
    app.run_server(debug=True)
