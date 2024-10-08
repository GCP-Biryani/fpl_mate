import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
#
CURR_GW = st.session_state.CURR_GW
#
players_df = pd.read_csv("data/players_data.csv")
picks_df = pd.read_csv('data/picks.csv')
picks_df = picks_df['element'].to_list()
#

# page config
st.set_page_config(
    page_title="Watchlist Graphs • FPL Mate", page_icon=":bar_chart:",layout="wide"
)
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
##############
st.markdown(
    "##### Watchlist based on: "
    + "Single performance indicator"
)
fig_xgi = px.bar(df_watchlist_xgi, x='web_name', y='expected_goal_involvements',color='expected_goal_involvements')
fig_form = px.bar(df_watchlist_form, x='web_name', y='form',color='form')
fig_ppg = px.bar(df_watchlist_ppg, x='web_name', y='points_per_game',color='points_per_game')
fig_ep = px.bar(df_watchlist_next_ep, x='web_name', y='ep_next',color='ep_next')
#
tab1, tab2, tab3, tab4 = st.tabs(["Expected Goal Involvements", "Form", "Points per Game", "Expected points - next gameweek"])
with tab1:
    st.plotly_chart(fig_xgi, theme="streamlit", use_container_width=False)
with tab2:
    st.plotly_chart(fig_form, theme="streamlit", use_container_width=False)
with tab3:
    st.plotly_chart(fig_ppg, theme="streamlit", use_container_width=False)
with tab4:
    st.plotly_chart(fig_ep, theme="streamlit", use_container_width=False)