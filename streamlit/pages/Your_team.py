import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import requests
import pandas as pd
#
# page config
st.set_page_config(
    page_title="Your Team stats • FPL Mate", page_icon=":bar_chart:",layout="wide"
)
#
CURR_GW = st.session_state.CURR_GW
team = pd.read_csv("team_id.csv")
team_id = team['team_id'][0]
#
players_df = pd.read_csv("players_data.csv")
#

# sidebar
with st.sidebar:
    st.markdown(""":chart_with_upwards_trend: :green[FPL]*Mate*""")
    st.caption(
        """Latest gameweek data: :blue["""
        + str(CURR_GW)
        + """]  
                [thecloudtechnologist](https://github.com/thecloudtechnologist)"""
    )

# landing
st.title(":soccer: :green[FPL]*Mate*")
st.divider()
# Get user picks
url = f"https://fantasy.premierleague.com/api/entry/{team_id}/event/{CURR_GW}/picks/"
response = requests.get(url)
data = response.json()
picks = data.get("picks", [])
picks_df = pd.DataFrame(picks)
picks_df.to_csv('picks.csv')
picks_df = picks_df['element'].to_list()

# User team Details & leagues
url = f"https://fantasy.premierleague.com/api/entry/{team_id}"
response = requests.get(url)
data = response.json()
first_name = data.get("player_first_name")
last_name = data.get("player_last_name")
player_name = first_name + " "+ last_name
team_name = data.get("name")
overall_points = data.get("summary_overall_points")
overall_rank = data.get("summary_overall_rank")
#
st.session_state.team_name = team_name
st.markdown(
    "##### Hello! :blue["
    + str(player_name)
    + """]

Your team name is : """
    + str(team_name)
    + "."
)
st.markdown(
    " Your team total points : :blue["
    + str(overall_points)
    + """]

Your team rank is : """
    + str(overall_rank)
    + "."
)

st.markdown(
    """**Your team performance stats**
"""
)

#
df_my_team = players_df[players_df.id.isin(picks_df)]
df_my_team = df_my_team[['web_name','element_type','now_cost','selected_by_percent','total_points','points_per_game','form','goals_scored','expected_goals','assists','expected_assists','expected_goal_involvements','goal_involvements','ep_next','clean_sheets','bonus','next_3','next_3_avg_FDRs','next_5','next_5_avg_FDRs']]
st.dataframe(df_my_team,hide_index=True,use_container_width=False,height=550,column_config={"web_name":"Name","element_type":"Position","now_cost":"Cost","selected_by_percent":"Selected by (%)","total_points":"Total points","points_per_game":"PPG","goals_scored":"GS","expected_goals":"xG","assists":"A","expected_assists":"xA","expected_goal_involvements":"xGI","goal_involvements":"actial Goal involvements","ep_next": "xP(next GW)","clean_sheets":"CS"})


st.markdown(
    """**Your team mini-league performance**
"""
)
# Classic Leagues
classic_df = pd.json_normalize(data['leagues']['classic'])
classic_df = classic_df[['name','entry_rank','entry_last_rank','entry_percentile_rank']]
st.dataframe(classic_df,hide_index=True,use_container_width=False)
#
get_watchlist = st.button("Click to get your watchlist")
if get_watchlist:
    switch_page("Watchlist")