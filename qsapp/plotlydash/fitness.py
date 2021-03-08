import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from datetime import date

from qsapp.visuals import render_body
from qsapp.helpers import Dates

import logging.config
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger("debugLogger")

logger.debug("Module fitness.py loaded")

body_layout = dbc.Container(
                [
                    dbc.Row([
                        dbc.Col(html.H1(children="Body & Activity", className="h2 pt-3 pb-3"), className="pl-0"),
                        dbc.Col([html.Small("Last: "),
                                 # TODO - dát to radši do rohu každé kartičky nebo jinam
                                 # html.Small(f"{(datetime.date(last_row_body.date.item())).strftime('%d-%m-%Y')}")],
                                 html.Small("XX-XX-XXXX")],
                                className="pt-3",width={"order": 12})
                    ]),
                    dbc.Row([
                        dbc.Row(
                            children="", id="body-cards"),

                        dbc.Col(
                            html.Div([
                            html.Div(
                                dcc.DatePickerRange(
                                    id='my-date-picker-range',
                                    month_format="MMMM YYYY",
                                    min_date_allowed=date(2006, 1, 1),
                                    display_format="DD/MM/YYYY",
                                    initial_visible_month=Dates.this_month_first,
                                    start_date=Dates.this_month_first,
                                    end_date=Dates.this_month_last,
                                    first_day_of_week=1,
                                ), className="float-right"
                            ),
                            html.Div(
                                    dcc.Dropdown(
                                            options= [
                                                {"label": "Lifetime", "value": "lifetime"},
                                                {"label": "This Month", "value": "thismonth"},
                                                {"label": "Last Month", "value": "lastmonth"},
                                                {"label": "This Week", "value": "thisweek"},
                                                {"label": "Last Week", "value": "lastweek"},
                                                {"label": "Last 90 Days", "value": "last90"},
                                                {"label": "Last 30 Days", "value": "last30"},
                                                {"label": "Last 7 Days", "value": "last7"},
                                                {"label": "Today", "value": "today"}
                                            ],
                                            id="time-period-picker",
                                            value="last30"
                                        ) , style={"width": "286px"}, className="float-right"

                            ),
                            html.Div(
                                dcc.Dropdown(
                                    options=[
                                        {"label": "Daily", "value": "D"},
                                        {"label": "Weekly", "value": "W"},
                                        {"label": "Monthly", "value": "M"},
                                        {"label": "Yearly", "value": "Y"},
                                    ],
                                    id="aggregation-picker",
                                    value="D"
                                ), style={"width": "286px"}, className="float-right"

                            )
                            ]), className="pr-0"
                        )
                    ], className="align-items-start"),

                    dbc.Row([
                        dbc.Row(
                        children="", id="energy-cards", className="justify-content-start pt-3"),
                        dbc.Col()
                    ]),

                    dbc.Row(
                        dbc.Col(
                            html.Div(
                                     [dcc.Graph(
                                        id='body-graph',
                                        figure=render_body("2020-12-01", "2020-12-31", "M"),
                                        config={"displayModeBar": False, "showTips": False}
                                     )
                                     ],
                            ), width=12, className="card shadow-sm"
                        ), className="pt-3"
                    ),
                    dbc.Row(
                        dbc.Col(

                        ), className="pt-3"
                    )
                ]
)