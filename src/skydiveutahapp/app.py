import datetime

import dash_bootstrap_components as dbc
import pytz
from components.footer import footerComponent
from components.header import headerComponent
from components.weather import weatherComponents
from components.webcam import webcamComponents
from components.winds import windsComponents
from dash import Dash, Input, Output, dcc, html
from pages import calendarPage, weatherPage, webcamPage, windsAloftPage
from pages import forecastPage

app = Dash(
    title="Skydive Utah Dashboard",
    external_stylesheets=[
        dbc.themes.MATERIA, 
        "https://fonts.googleapis.com/css?family=Dosis:200,400,500,600"],
    name=__name__,
    update_title=None,
    suppress_callback_exceptions=True,
)

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Div(id='hidden-div-callbacks', style={'display': 'hidden'}),
        # Refresh interval component - refreshes components every 60 seconds
        dcc.Interval(id='refresh-interval', interval=1000*60, n_intervals=0),
        html.Div(id='header-container', children=headerComponent.render()),
        html.Div(
            id='page-content',
            style={
                "padding": "2rem 1rem",
            },
        ),
        html.Div(id='footer-container', children=footerComponent.render())
    ]
)

server = app.server

########################
###### CALLBACKS #######
########################


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"))
def router(pathname):
    if pathname == "/":
        return [weatherPage.render()]
    elif pathname == "/winds":
        return [windsAloftPage.render()]
    elif pathname == "/calendar":
        return [calendarPage.render()]
    elif pathname == "/webcam":
        return [webcamPage.render()]
    elif pathname == "/forecast":
        return [forecastPage.render()]
    else:
        return [dcc.Location(pathname="/", id='redirect')]


@app.callback(
    Output("live-clock", "children"),
    Input("header-interval", "n_intervals"),
)
def update_time(n):
    dt_utc = datetime.datetime.now()
    # Change from MST to America/Denver
    dt_mst = dt_utc.astimezone(pytz.timezone("America/Denver"))
    return f'{dt_mst.strftime("%a %m/%d %I:%M:%S %p")} MST'


@app.callback(
    Output("footer-container", "children"),
    Input("refresh-interval", "n_intervals"),
)
def update_footer(n):
    return footerComponent.render()


@app.callback(
    Output("weather-page-container", "children"),
    Input("refresh-interval", "n_intervals"))
def refresh_weather(refresh):
    return weatherComponents.getAllComponents()


@app.callback(
    Output("winds-page-container", "children"),
    Input("refresh-interval", "n_intervals"),
)
def refresh_winds(refresh):
    return windsComponents.getAllComponents()


@app.callback(
    Output("webcam-page-container", "children"),
    Input("refresh-interval", "n_intervals"),
)
def refresh_winds(refresh):
    return webcamComponents.getAllComponents()


if __name__ == "__main__":
    # print('TODO:')
    # print('\t- Calendar iFrame src')
    # print('\t- Loading spinner component that doesnt run on each callback update')

    # Improvement: Winds direction graph - wrap around wind normalize around mean to be continuous
    # Improvement: App - HTTP graceful error handling
    # Improvement: Winds Forecast - if you pull the forecast at 2:50pm MDT, that's 20:50 UTC, so it used the forecast issued for 20Z. Ideally, you'd want to use 21Z at the point, which you can get by setting hourOffset=1
    # not sure if you want to bother with adding a condition on whether the current time is before or after :30
    app.run_server(debug=True, port=8050)
