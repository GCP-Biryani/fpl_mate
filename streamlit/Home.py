import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
import requests
import subprocess
import sys
import os


url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
r = requests.get(url)
json1 = r.json()
events_df = pd.DataFrame(json1['events'])
CURR_GW = events_df.loc[events_df['is_current'] == True]['id'].iloc[-1]
#
st.session_state.CURR_GW = CURR_GW
# page config
st.set_page_config(
    page_title="Home • FPL Mate", page_icon=":soccer:",layout="wide"
)

# sidebar
with st.sidebar:
    st.markdown(""":soccer: :green[FPL]*Mate*""")
    st.caption(
        """Latest gameweek data: :blue["""
        + str(CURR_GW)
        + """]  
                [thecloudtechnologist](https://github.com/thecloudtechnologist)"""
    )


# landing
st.title(":soccer: :green[FPL]*Mate*")
st.markdown(
    """**Welcome to FPL Mate - Your Ultimate Fantasy Premier League Mate!**

FPL mate will help you analyse your team and recommend watchlist based on factors like expected goal involvements, form, points per game, next week expected points and ICT rank
"""
)

# latest gameweek
st.markdown(
    "##### Latest data from Gameweek :blue["
    + str(CURR_GW)
    + """] 
Use our latest data, stats, and models to prepare your team for success in :blueGameweek """
    + str(CURR_GW + 1)
    + "."
)

# development updates
st.markdown(
"""##### What stats are provided?
    - Your players data with points, goals, xG, assists, xA, GI, xGI, form, PPM, next 3 matches, average FDR
    - Top-10 watchlist based on expected goal involvements
    - Top-10 watchlist based on form
    - Top-10 watchlist based on points per game
    - Top-10 watchlist based on ICT
    - Top-10 watchlist based on multiple factors (best of the list)
    """
)
# Create data directory
if not os.path.exists('data'):
   os.makedirs('data')
#
st.markdown(
"""##### 	:hourglass_flowing_sand:
    Please wait , while the data is being loaded from FPL API, Once data is loaded, you'll see text box to enter your FPL ID, to analyse your team
    """
)
# Get data
subprocess.run([f"{sys.executable}", "streamlit/get_data.py"])
#
st.markdown(":white_check_mark:")
#
team_id = st.text_input("Enter your FPL ID")
if 'team_id' not in st.session_state:
    st.session_state.team_id = team_id
#
#
enter_analysis = st.button("Click to get started")
if enter_analysis:
    switch_page("Your_team")