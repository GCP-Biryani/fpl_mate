import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd

#
CURR_GW = st.session_state.CURR_GW
#
players_df = pd.read_csv("data/players_data.csv")
picks_df = pd.read_csv('data/picks.csv')
picks_df = picks_df['element'].to_list()
#
# page config
st.set_page_config(
    page_title="Your Watchlist • FPL Mate", page_icon=":eye:",layout="wide"
)
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
##############
# Watchlist
df_watchlist=players_df[~players_df.id.isin(picks_df)]
df_watchlist = df_watchlist[['web_name','element_type','now_cost','selected_by_percent','total_points','points_per_game','form','goals_scored','expected_goals','assists','expected_assists','expected_goal_involvements','goal_involvements','ep_next','clean_sheets','bonus','ict_index_rank','next_3','next_3_FDRs','next_3_avg_FDRs','next_5','next_5_FDRs','next_5_avg_FDRs','team']]
#
df_watchlist_xgi = df_watchlist.sort_values('expected_goal_involvements',ascending=False).head(10)
df_watchlist_xgi = df_watchlist_xgi[['web_name','element_type','now_cost','selected_by_percent','total_points','goals_scored','expected_goals','assists','expected_assists','expected_goal_involvements','goal_involvements']]
df_watchlist_xgi_names = df_watchlist_xgi['web_name']
#
df_watchlist_form = df_watchlist.sort_values('form',ascending=False).head(10)
df_watchlist_form = df_watchlist_form[['web_name','element_type','now_cost','selected_by_percent','total_points','form','goals_scored','assists','goal_involvements']]
df_watchlist_form_names = df_watchlist_form['web_name']
#
df_watchlist_ppg = df_watchlist.sort_values('points_per_game',ascending=False).head(10)
df_watchlist_ppg = df_watchlist_ppg[['web_name','element_type','now_cost','selected_by_percent','total_points','points_per_game','goals_scored','assists','goal_involvements']]
df_watchlist_ppg_names = df_watchlist_ppg['web_name']
#
df_watchlist_ict = df_watchlist.sort_values('ict_index_rank',ascending=True).head(10)
df_watchlist_ict = df_watchlist_ict[['web_name','element_type','now_cost','selected_by_percent','total_points','goals_scored','expected_goals','assists','expected_assists','expected_goal_involvements','goal_involvements','bonus','ict_index_rank']]   
df_watchlist_ict_names = df_watchlist_ict['web_name']
#
df_watchlist_next_ep = df_watchlist.sort_values('ep_next',ascending=False).head(10)
df_watchlist_next_ep = df_watchlist_next_ep[['web_name','element_type','now_cost','selected_by_percent','total_points','ep_next','goals_scored','expected_goals','assists','expected_assists','expected_goal_involvements','goal_involvements']]
#
df_watchlist_names = pd.concat([df_watchlist_xgi_names,df_watchlist_ppg_names,df_watchlist_form_names,df_watchlist_ict_names])
df_watchlist_names = df_watchlist_names.unique()
df_watchlist_stats = players_df[players_df.web_name.isin(df_watchlist_names)]
df_watchlist_table = df_watchlist_stats[['web_name','team','position','now_cost','expected_goal_involvements','form','points_per_game','ict_index_rank','next_3_avg_FDRs','next_5_avg_FDRs']]
# 
# #############
st.markdown(
    "##### Multi-factor watchlist recommondations: :green["
    + "XGI, Form, PPG, ICT Index ranking & FDR"
    + """] 
Click on any column to sort by that stat """
)
st.dataframe(df_watchlist_table,hide_index=True,use_container_width=False,height=1025,width=1200)

#
#
get_graphs = st.button("Click to see analysis graphs")
if get_graphs:
    switch_page("Graphs")