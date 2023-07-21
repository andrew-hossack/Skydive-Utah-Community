import json

import requests
from dash import dash_table, dcc, html
from plotly.graph_objs import Scatter

from utils import timeUtils


def _get_data():
    # Getting the data from the url
    url = 'https://markschulze.net/winds/winds.php?lat=40.61318686&lon=-112.3481226&hourOffset=0%3F&referrer=SkydiveUtah'
    response = requests.get(url)
    return json.loads(response.text)


def _render_table(data) -> dash_table.DataTable:
    # Prepare data for the table
    table_data = [dict(Altitude=f'{altFt} Ft',
                       Direction=f"{data['direction'][str(altFt)]}°",
                       Speed=f"{data['speed'][str(altFt)]} Kts",
                       Temperature=f"{data['temp'][str(altFt)]}°C")
                  for altFt in data['altFt'] if altFt <= 20000]

    # Convert temperature to Fahrenheit
    for row in table_data:
        tempC = float(row['Temperature'][:-2])
        tempF = tempC * (9/5) + 32
        row['Temperature'] = f"{int(tempF)}°F"

    # Create the table
    return dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in table_data[0]],
        data=table_data,
        style_table={'maxWidth': '80vw',
                     'border': 'thin lightgrey solid', 'overflow': 'scroll'},
        style_header={
            'backgroundColor': 'rgba(47, 62, 70, 1)',
            'fontWeight': 'bold',
            'color': 'white'
        },
        style_cell={'textAlign': 'left',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '0px', 'maxWidth': '180px',
                    'whiteSpace': 'normal',
                    'backgroundColor': 'rgba(47, 62, 70, 0)',
                    'color': 'white'},
        style_data={'whiteSpace': 'normal'},
        css=[{
            'selector': '.dash-cell div.dash-cell-value',
            'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
        }],
    )


def _resolve_wind_direction(data: dict, altitudes: list) -> list[list]:
    # This method probably sucks, I used chatgpt for help lol
    wrapped_altitudes = []
    wrapped_wind_dirs = []
    dir_data = [data['direction'][str(alt)] for alt in altitudes]

    temp_alts = [altitudes[0]]
    temp_dirs = [dir_data[0]]
    for i in range(1, len(dir_data)):
        if abs(dir_data[i] - dir_data[i-1]) > 180:
            wrapped_altitudes.append(temp_alts)
            wrapped_wind_dirs.append(temp_dirs)
            temp_alts = [altitudes[i]]
            temp_dirs = [dir_data[i]]
        else:
            temp_alts.append(altitudes[i])
            temp_dirs.append(dir_data[i])
    wrapped_altitudes.append(temp_alts)
    wrapped_wind_dirs.append(temp_dirs)

    return wrapped_altitudes, wrapped_wind_dirs


def renderWindsAloft() -> html.Div:
    data = _get_data()

    # # UNCOMMENT FOR "DISJOINTED" WIND DIRECTION TEST DATA
    # ##############
    # # Wrap right
    # wind_dir = [70, 80, 90, 100, 110, 120, 130, 140, 150, 200,
    #             250, 300, 350, 50, 60, 70, 80, 90, 95, 100, 100]

    # # Wrap left
    # # wind_dir = [150, 140, 140, 130, 110, 100, 100, 100, 50, 350,
    # #             300, 280, 250, 240, 180, 160, 140, 120, 110, 100, 100]

    # # Here we have a shortened list, let's just fit it with altitude <= 20000
    # new_directions = {altitude: direction
    #                   for (altitude, direction) in zip([key for key in data['direction'] if int(key) <= 20000], wind_dir)}

    # # Then we replace the corresponding parts in original data with new directions
    # data['direction'].update(new_directions)
    # ##############

    altitude_list = [altFt for altFt in data['altFt'] if altFt <= 20000]

    wind_speed_trace = Scatter(y=[altFt for altFt in data['altFt'] if altFt <= 20000],
                               x=[data['speed'][str(altFt)]
                                  for altFt in data['altFt'] if altFt <= 20000],
                               mode='lines',
                               name='Wind Speed (Kts)',
                               line=dict(color='coral'))

    altitudes_by_trace, winds_by_trace = _resolve_wind_direction(
        data, altitude_list)
    wind_dir_traces = [Scatter(y=altitudes_by_trace[i],
                               x=winds_by_trace[i],
                               mode='lines',
                               xaxis='x2' if i % 2 == 0 else 'x3',
                               name='Wind Direction (°)',
                               showlegend=True if i == 0 else False,
                               line=dict(shape='linear'),
                               marker=dict(color='mintcream'))
                       for i in range(len(altitudes_by_trace))]

    tickrange = [min(int(value) for value in data['direction'].values()), max(
        int(value) for value in data['direction'].values())]
    tickvals = [i for i in range(min(tickrange), max(tickrange) + 1, 30)]
    ticktext = [f"{i%360}°" for i in tickvals]

    return html.Div(
        style={
            'padding': '20px',
            'margin': '20px',
            'backgroundColor': 'rgba(47, 62, 70, 0.5)',
            'fontSize': '20px',
            'color': 'black',
            'borderRadius': '15px',
            'boxShadow': '0 0 1px 5px rgba(47,62,70,0.5)',
            'width': '80vw'
        },
        children=[
            html.H2('Winds Aloft',
                    style={
                        'textAlign': 'center',
                        'fontSize': '26px',
                        'color': '#3498db'
                    }),
            html.Div(children=f'Last reported at {timeUtils.zulu_to_mst_string(data["validtime"])}',
                     style={
                         'textAlign': 'center', 'color': 'white'}),
            dcc.Graph(
                id='example-graph',
                style={'width': '100%', 'display': 'inline-block'},
                figure=dict(
                    data=[wind_speed_trace, *wind_dir_traces],
                    layout=dict(
                        xaxis=dict(title='Wind Speed (Kts)',
                                   showgrid=True,
                                   gridcolor='rgba(255, 255, 255, 0.2)',
                                   color='coral',
                                   showline=False,
                                   linecolor='coral',
                                   fixedrange=True),
                        xaxis2=dict(title='Wind Direction (°)',
                                    overlaying='x',
                                    side='top',
                                    showgrid=False,
                                    gridcolor='rgba(255, 255, 255, 0.2)',
                                    range=tickrange,
                                    tickvals=tickvals,
                                    ticktext=ticktext,
                                    color='mintcream',
                                    showline=False,
                                    linecolor='mintcream',
                                    fixedrange=True),
                        xaxis3=dict(overlaying='x', side='bottom',
                                    showgrid=False,
                                    range=tickrange,
                                    tickvals=tickvals,
                                    ticktext=ticktext,
                                    color='mintcream',
                                    showline=False,
                                    showticklabels=False,
                                    fixedrange=True),
                        yaxis=dict(title='Altitude',
                                   showgrid=True,
                                   gridcolor='rgba(255, 255, 255, 0.2)',
                                   fixedrange=True),
                        hovermode="x",
                        template='plotly_dark',
                        plot_bgcolor='rgba(47, 62, 70, 0)',
                        paper_bgcolor='rgba(47, 62, 70, 0)',
                        font={'color': 'white'},
                        legend={'traceorder': 'reversed', 'y': 1,
                                'x': 0, 'bgcolor': 'rgba(0,0,0,0)'},
                        autosize=True,
                    )
                ),
                config=dict(displayModeBar=False),
            ),

            html.Div(_render_table(data), style={'paddingTop': '20px'}),
            dcc.Markdown('''
            Credit to Mark Schulze ([markschulze.net/winds](http://markschulze.net/winds)) for providing API access to winds aloft data.
            ''', style={'color': 'white', 'font-size': '12px','margin-top':'10px'})
        ]
    )


def getAllComponents() -> list[html.Div]:
    return [renderWindsAloft()]
