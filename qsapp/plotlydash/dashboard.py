import dash
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from datetime import date

from qsapp.visuals import render_body, CardBody, CardEnergy
from qsapp.helpers import Dates
from .layout import html_layout
from .body import body_layout
from .test import test_layout

import logging.config
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger("debugLogger")

logger.debug("Module dashboard.py loaded")

def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app: Dash = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        suppress_callback_exceptions=True,
        external_stylesheets=[
            '/static/css/bootswatch.css', '/static/css/custom.css'
        ]
    )

    # Custom HTML layout
    dash_app.index_string = html_layout

    dash_app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])

    init_callbacks(dash_app)

    return dash_app.server

def init_callbacks(dash_app):
    @dash_app.callback(dash.dependencies.Output('body-graph', 'figure'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date'),
     dash.dependencies.Input('aggregation-picker', 'value')])
    def update_output(start_date, end_date, aggregation):
        return render_body(start_date,end_date, aggregation)

    @dash_app.callback([dash.dependencies.Output('my-date-picker-range', 'start_date'),
     dash.dependencies.Output('my-date-picker-range', 'end_date')],
     dash.dependencies.Input('time-period-picker', component_property='value'))
    def update_timeperiod(input):
        if input == "thismonth":
            start_date = Dates.this_month_first
            end_date = Dates.this_month_last
        elif input == "lastmonth":
            start_date = Dates.last_month_first
            end_date = Dates.last_month_last
        elif input == "thisweek":
            start_date = Dates.this_monday
            end_date = Dates.this_sunday
        elif input == "lastweek":
            start_date = Dates.last_monday
            end_date = Dates.last_sunday
        elif input == "lifetime":
            start_date = date(2006, 1, 1)
            end_date = Dates.now
        elif input == "last90":
            start_date = Dates.last_90_days
            end_date = Dates.now
        elif input == "last30":
            start_date = Dates.last_30_days
            end_date = Dates.now
        elif input == "last7":
            start_date = Dates.last_7_days
            end_date = Dates.now
        elif input == "today":
            start_date = Dates.now
            end_date = Dates.now
        else:
            start_date = Dates.last_30_days
            end_date = Dates.now
        return start_date, end_date

    @dash_app.callback(dash.dependencies.Output('body-cards', 'children'),
                       [dash.dependencies.Input('my-date-picker-range', 'start_date'),
                        dash.dependencies.Input('my-date-picker-range', 'end_date')])
    def update_body_cards(start_date, end_date):
        return [CardBody("weight", "non").get_values(start_date, end_date),
                CardBody("muscle_mass", "positive").get_values(start_date, end_date),
                CardBody("fat_mass_weight", "negative").get_values(start_date, end_date)]

    @dash_app.callback(dash.dependencies.Output('energy-cards', 'children'),
                       [dash.dependencies.Input('my-date-picker-range', 'start_date'),
                        dash.dependencies.Input('my-date-picker-range', 'end_date')], prevent_initial_call=True)
    def update_energy_cards(start_date, end_date):
        return [CardEnergy("energy_output", "positive").get_values(start_date, end_date),
                CardEnergy("energy_income", "negative").get_values(start_date, end_date),
                CardEnergy("energy_total", "positive").get_values(start_date, end_date)]

    @dash_app.callback(dash.dependencies.Output('page-content', 'children'),
                  [dash.dependencies.Input('url', 'pathname')])
    def display_page(pathname):
        if pathname == '/dashapp/body':
            return body_layout
        elif pathname == '/dashapp/test':
            return test_layout
        else:
            pass
