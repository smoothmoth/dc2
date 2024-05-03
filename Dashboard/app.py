import dash
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR])

# Customize Layout
app.layout = dbc.Container([
    # header
    dcc.Markdown("Data Challenge 2", style={'fontSize': 45, 'textAlign': 'center'}),

    # Short instructions for use
    dbc.Row([
        dbc.Col([
            html.Center(dcc.Markdown("Areas at risk of low trust and confidence")),
        ], width={"size": 8, "offset": 2}, align="centre")
    ], justify="centre"),

], fluid=True)

# Run App
if __name__ == '__main__':
    app.run_server(port=8051, debug=False, use_reloader=False)
