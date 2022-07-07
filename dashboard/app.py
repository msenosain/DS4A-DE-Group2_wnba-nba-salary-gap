import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import sqlalchemy
import os
from pathlib import Path
from typing import Tuple, Optional
from dash.dependencies import Input, Output, State

dirname = os.path.dirname(__file__)
path = os.path.join(dirname, "data/")

#data_nba_wnba = pd.read_csv(path + 'cleaned_data_wnba_nba_2019.csv')
data_nba_wnba = pd.read_csv('data/cleaned_data_wnba_nba_2019.csv')
league_rev = pd.read_csv('data/league_revenue.csv')

## MODIFY NUMBER FORMAT
def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'),
                         ['', 'K', 'M', 'B', 'T'][magnitude])


# Buttons at the begining 
radio_league = dbc.RadioItems(
    id="radio_league",
    className="radio",
    options=[
        dict(label="WNBA", value=0),
        dict(label="NBA", value=1),
        dict(label="Both", value=2),
    ],
    value=2,
    inline=True,
)                         

# Dropdown menu for stats
drop_stats = dcc.Dropdown(
    id="drop_stats",
    clearable=False,
    searchable=False,
    options=[
        {"value":"G",  "label":"Games"},
        {"value":"GS", "label":"Games Started"},
        {"value":"MP", "label":"Minutes Played"},
        {"value":"FG", "label":"Field Goals"},
        {"value":"FGA", "label":"Field Goals Attempts"},
        {"value":"FG%", "label":"Field Goal Percentage"},
        {"value":"3P", "label":"3-Point Field Goals"},
        {"value":"3PA", "label":"3-Point Field Goal Attempts"},
        {"value":"3P%", "label":"3-Point Field Goal Percentage"},
        {"value":"2P", "label":"2-Point Field Goals"},
        {"value":"2PA", "label":"2-Point Field Goal Attempts"},
        {"value":"2P%", "label":"2-Point Field Goal Percentage"},
        {"value":"FT", "label":"Free Throws"},
        {"value":"FTA", "label":"Free Throw Attempt"},
        {"value":"FT%", "label":"Free Throw Percentage"},
        {"value":"ORB", "label":"Offensive Rebounds"},
        {"value":"TRB", "label":"Total Rebounds"},
        {"value":"AST", "label":"Assits"},
        {"value":"STL", "label":"Steals"},
        {"value":"BLK", "label":"Blocks"},
        {"value":"TOV", "label":"Turnovers"},
        {"value":"PF", "label":"Personal Fouls"},
        {"value":"PTS", "label":"Points"},
    ],
    value="G",
    style={"margin": "4px", "box-shadow": "0px 0px #ebb36a", "border-color": "#ebb36a"},
)

########################################################
# DASH
########################################################

def Header(name, app):
    title = [
        html.H1(name, style={"margin-top": 30, "font-size":50}),
        html.P(
            """
            After over half a century since the Equal Pay Act was passed in the US 
            women still face issues of gender pay gap across various job spectrums 
            today. The WNBA, especially in recent years, have  been vocal about the 
            unfair compensation compared to their male counterparts. Their advocacy 
            for equal pay is not a cry for these women athletes to necessarily earn 
            the same as their male counterparts but more importantly for fair 
            compensation based on generated revenue and shared ratios.
            """
        ),
        html.P("Note: Data presented here corresponds to 2019 season.",
            style={"font-size":12, "font-style": "italic"}),
    ]
    logo = [
        html.Img(
        src=app.get_asset_url("WNBA_logo.png"), style={"float": "right", "height": 110,
        "margin-top": 15}
        ),
        html.Img(
        src=app.get_asset_url("NBA_logo.png"), style={"float": "right", "height": 110,
        "margin-top": 15}
        ),
    ]

    return dbc.Row([dbc.Col(title, md=9), dbc.Col(logo, md=3)])



# Start the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
  
# Card components
cards = [
    dbc.Card(
        [
            html.H2(human_format(league_rev['total_year_revenue'][0]), className="card-title"),
            html.P("WNBA Total Revenue", className="card-text"),
        ],
        body=True,
        color="#F57B20",
        inverse=True,
        style={'height':'14vh'}
    ),
    dbc.Card(
        [
            html.H2(league_rev['revenue_share_ratio'][0], className="card-title"),
            html.P("WNBA Share Ratio to Players Salaries", className="card-text"),
        ],
        body=True,
        color="#F57B20",
        inverse=True,
        style={'height':'14vh'}
    ),
    dbc.Card(
        [
            html.H2(human_format(league_rev['total_year_revenue'][1]), className="card-title"),
            html.P("NBA Total Revenue", className="card-text"),
        ],
        body=True,
        color="#17408B",
        inverse=True,
        style={'height':'14vh'}
    ),
    dbc.Card(
        [
            html.H2(league_rev['revenue_share_ratio'][1], className="card-title"),
            html.P("NBA Share Ratio to Players Salaries", className="card-text"),
        ],
        body=True,
        color="#17408B",
        inverse=True,
        style={'height':'14vh'}
    ),
]





app.layout = dbc.Container(
    [
        Header("WNBA/NBA Salary Gap", app),
        html.Hr(),
        dbc.Row([dbc.Col(card) for card in cards]),
        html.Br(),
        dbc.Row([
            dbc.Col(html.Div(
                [
                    html.Label("Choose League:"),
                    html.Br(),
                    html.Br(),
                    radio_league,
                ],
                className="box",
            )),
            dbc.Col(html.Div(
                [
                    html.Label("Choose stat: "),
                    drop_stats,
                ],
                className="box",
            ))
        ]),
        dbc.Row([
            dbc.Col(html.Div(
                [
                    dcc.Graph(id="fig_stat"),
                ]
            )),
            dbc.Col(html.Div(
                [
                    dcc.Graph(id="fig_salary"),
                ]
            )),
        ]),
    ],
    fluid=False,
)

########################################################
# CALLBACKS
########################################################
@app.callback(
    [
        Output("fig_stat", "figure"),
        Output("fig_salary", "figure"),
    ],
    [
        Input("radio_league", "value"),
        Input("drop_stats", "value")
    ]
)


def top10players_bystat(league_val, stat):
    # Filter by League
    if league_val == 0:
        df = data_nba_wnba[data_nba_wnba["League"] == "WNBA"]
    if league_val == 1:
        df = data_nba_wnba[data_nba_wnba["League"] == "NBA"]
    if league_val == 2:
        df = data_nba_wnba

    # Filter and sort by stat
    df = (
        df[["Player", "League", "Team", "Pos", "salary", stat]]
        .sort_values(stat, axis=0, ascending=False)
        .head(10)
    )

    # Plot by stat
    fig_stat = px.bar(
        df.sort_values(stat),
        y="Player",
        x=stat,
        color="League",
        hover_data=["League", "Team", "Pos"],
        color_discrete_map={"WNBA": "#F57B20", "NBA": "#17408B"},
    )
    fig_stat.update_layout(
        title_text="Top 10 players by chosen stat",
        showlegend=False,
        title_font_size=22,
        title_x=0.5,
        title_y=0.92,
        yaxis=dict(
            title=None,
            titlefont_size=16,
            tickfont_size=11,
        ),
        xaxis=dict(
            title=stat,
            titlefont_size=16,
            tickfont_size=11,
        ),
    )
    # Plot by salary
    fig_salary = px.bar(
        df.sort_values(stat),
        y="Player",
        x="salary",
        color="League",
        hover_data=["League", "Team", "Pos"],
        color_discrete_map={"WNBA": "#F57B20", "NBA": "#17408B"},
    )
    fig_salary.update_layout(
        title_text="Salary of top 10 players by chosen stat",
        showlegend=False,
        title_font_size=22,
        title_x=0.5,
        title_y=0.92,
        yaxis=dict(
            title=None,
            titlefont_size=16,
            tickfont_size=11,
        ),
        xaxis=dict(
            title="USD",
            titlefont_size=16,
            tickfont_size=11,
        ),
    )

    return fig_stat, fig_salary

########################################################
# RUN APP
########################################################

if __name__ == '__main__':
    app.run_server(debug=True)

