import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import logging.config

import dash_html_components as html
import dash_bootstrap_components as dbc

from qsapp.models import Body, Total_Energy
from qsapp.helpers import Dates

logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
logger = logging.getLogger("debugLogger")

logger.debug("Module visuals loaded")

def render_body(startdate, enddate, aggregation):
    df = Body.load_df()
    mask = (df.date >= startdate) & (df.date <= enddate)
    df = df.loc[mask]
    df.index = df.date
    df = df.groupby(pd.Grouper(freq=aggregation)).mean()
    y1 = df.weight
    y2 = df.muscle_mass
    y3 = df.fat_mass_weight

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.01)
    fig.append_trace(go.Scatter(x=df.index, y=y1,
                                mode='lines+markers',
                                line={"shape": "spline", "color": "#6610f2"},
                                hoverinfo="text",
                                hovertemplate="<b>Weight:</b> <br> %{y:.2f)} kg<extra></extra>",
                                connectgaps=True
                                ), row=1, col=1)

    fig.append_trace(go.Scatter(x=df.index, y=y2,
                                mode='lines+markers',
                                line={"shape": "spline", "color": "#20c997"},
                                hoverinfo="text",
                                hovertemplate="<b>Muscle Mass:</b> <br> %{y:.2f)} kg<extra></extra>",
                                connectgaps=True
                                ), row=2, col=1)

    fig.append_trace(go.Scatter(x=df.index, y=y3,
                                mode='lines+markers',
                                line={"shape": "spline", "color": "#eb6864"},
                                hoverinfo="text",
                                hovertemplate="<b>Fat Mass Weight:</b> <br> %{y:.2f)} kg<extra></extra>",
                                connectgaps=True
                                ), row=3, col=1)

    fig.update_layout(showlegend=False,
                      margin={"t": 10, "l": 0, "r": 0, "b": 40},
                      plot_bgcolor="white",
                      hovermode="x unified",
                      height=500
                      )

    fig.update_traces(xaxis='x3', row=1, col=1)
    fig.update_traces(xaxis='x3', row=2, col=1)
    fig.update_traces(xaxis='x3', row=3, col=1)

    fig.update_yaxes(range=[y1.min() - 0.1, y1.max() + 1], row=1, col=1)
    fig.update_yaxes(range=[y2.min() - 0.1, y2.max() + 0.1], row=2, col=1)
    fig.update_yaxes(range=[y3.min() - 1, y3.max() + 0.1], row=3, col=1)

    if aggregation == "D" or aggregation == "W":
        fig.update_xaxes(tickformat="%d-%m-%y")
    elif aggregation == "M":
        fig.update_xaxes(tickformat="%m-%Y")
    elif aggregation == "Y":
        fig.update_xaxes(tickformat="%Y", ticklabelmode="period")

    return fig


def render_energy_barchart(startdate, enddate, aggregation):
    df = Total_Energy.load_df()
    mask = (df.date >= startdate) & (df.date <= enddate)
    df = df.loc[mask]
    df.index = df.date
    df = df.groupby(pd.Grouper(freq=aggregation)).mean()

    fig = go.Figure([go.Bar(x=df.index, y=df.active_energy)])

    fig.update_layout(showlegend=False,
                      margin={"t": 10, "l": 0, "r": 0, "b": 40},
                      plot_bgcolor="white",
                      hovermode="x unified",
                      height=300
                      )

    if aggregation == "D" or aggregation == "W":
        fig.update_xaxes(tickformat="%d-%m-%y")
    elif aggregation == "M":
        fig.update_xaxes(tickformat="%m-%Y")
    elif aggregation == "Y":
        fig.update_xaxes(tickformat="%Y", ticklabelmode="period")

    return fig


class Card(object):
    def __init__(self, metric, trend, datasource, unit, format):
        self.metric = metric
        self.metric_name = self.metric.replace("_", " ")
        self.metric_name = self.metric_name.title()
        self.trend = trend
        self.unit = unit
        self.format = format

        self.datasource = datasource

    def get_values(self, startdate, enddate):
        mask_original = (self.datasource.date >= startdate) & (self.datasource.date <= enddate)
        df_original = self.datasource.loc[mask_original]
        previous_startdate, previous_enddate = Dates.count_previous_period(startdate, enddate)
        mask_previous = (self.datasource.date >= previous_startdate) & (self.datasource.date <= previous_enddate)
        df_previous = self.datasource.loc[mask_previous]
        original_value = df_original[self.metric].mean()
        previous_value = df_previous[self.metric].mean()
        change = original_value - previous_value
        change = f"{self.format}".format(change)
        if float(change) >= 0:
            change = f"+{change}"

        if self.trend == "non":
            cardchange = "cardchange"
        elif self.trend == "positive" and float(change) >= 0:
            cardchange = "cardchange-p"
        elif self.trend == "positive" and float(change) < 0:
            cardchange = "cardchange-n"
        elif self.trend == "negative" and float(change) >= 0:
            cardchange = "cardchange-n"
        elif self.trend == "negative" and float(change) < 0:
            cardchange = "cardchange-p"

        return dbc.Col(
            html.Div(children=
            html.Div([
                html.H5(children=self.metric_name),
                html.Div([
                    html.H3(f"{self.format}".format(original_value) + f" {self.unit}", className="cardnumber"),
                    html.P(f"{change} {self.unit}", className=cardchange)]),
            ], className="card-body pb-1"), className="card shadow-sm", style={"width": "16rem"}
            )
        )


class CardBody(Card):
    unit = "kg"
    format = "{:.2f}"

    def __init__(self, metric, trend, datasource):
        Card.__init__(self, metric, trend, datasource, self.unit, self.format)


class CardEnergy(Card):
    unit = "kcal"
    format = "{:.0f}"

    def __init__(self, metric, trend, datasource):
        Card.__init__(self, metric, trend, datasource, self.unit, self.format)

