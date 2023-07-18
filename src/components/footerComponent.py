from dash import html

from utils import weatherUtils


def render() -> html.Div:
    currentMetar = weatherUtils.get_metar()
    return html.Div([
        html.Footer([
            f'{currentMetar.code}',
            html.A(' View Raw METAR', href='https://www.aviationweather.gov/metar/data?ids=ktvy&format=decoded&hours=1&taf=off&layout=on', target='_blank')
        ], style={
            'textAlign': 'center',
            'paddingTop': '10px',
            'backgroundColor': 'rgba(51, 51, 51, 0.8)',
            'position': 'fixed',
            'bottom': '0',
            'height': '10px',
            'paddingBottom': '20px',
            'width': '100%',
            'fontSize': '10px',
            'color': 'white',
            'zIndex': '998',
        })
    ])