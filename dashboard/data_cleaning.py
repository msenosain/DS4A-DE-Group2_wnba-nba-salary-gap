import pandas as pd
import os
from pathlib import Path

# data from
# https://www.basketball-reference.com/leagues/NBA_2019_totals.html#totals
# https://www.basketball-reference.com/wnba/years/2019_totals.html#totals

# Read datasets
wnba_salary = pd.read_csv("data/cleaned_wnba_player_salary_data.csv")
nba_salary = pd.read_csv("data/cleaned_nba_player_salary_data.csv")
wnba_stats = pd.read_csv("data/WNBA_pergamestats_2019.csv")
nba_stats = pd.read_csv("data/NBA_pergamestats_2019.csv")

# Clean Player names in wnba_stats
wnba_stats["Player"] = wnba_stats["Player"].str.replace("</strong", "")

# Clean player names in salary dfs
nba_salary["Player"] = nba_salary["first_name"] + " " + nba_salary["last_name"]
wnba_salary["Player"] = wnba_salary["first_name"] + " " + wnba_salary["last_name"]

# Join datasets
nba_complete = (
    nba_salary.set_index("Player")
    .join(nba_stats.set_index("Player"), how="inner")
    .reset_index()
)
wnba_complete = (
    wnba_salary.set_index("Player")
    .join(wnba_stats.set_index("Player"), how="inner")
    .reset_index()
)

# rename teams column in nba df
nba_complete.rename(columns={"Tm": "Team"}, inplace=True)

# Add league information
nba_complete["League"] = "NBA"
wnba_complete["League"] = "WNBA"

# homogenize columns
column_names = [
    "Player",
    "League",
    "Team",
    "Pos",
    "salary",
    "G",
    "GS",
    "MP",
    "FG",
    "FGA",
    "FG%",
    "3P",
    "3PA",
    "3P%",
    "2P",
    "2PA",
    "2P%",
    "FT",
    "FTA",
    "FT%",
    "ORB",
    "TRB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "PF",
    "PTS",
]
nba_complete = nba_complete[column_names]
wnba_complete = wnba_complete[column_names]

nba_wnba = pd.concat([nba_complete, wnba_complete])

nba_wnba.to_csv("data/statspergame_salary_wnba_nba_2019.csv", index=False)