# %%
import requests
import pandas as pd
import numpy as np
from tabulate import tabulate
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly import data
pd.options.mode.chained_assignment = None

# %%
# Input team ID
team_id = input("Enter your FPL ID:")
#
players_unused_columns = ['chance_of_playing_next_round','chance_of_playing_this_round','code','cost_change_event','cost_change_event_fall','cost_change_start','cost_change_start_fall','in_dreamteam','special','squad_number','transfers_in','transfers_in_event','transfers_out','transfers_out_event','region','influence_rank_type','creativity_rank_type','threat_rank_type','ict_index_rank_type','corners_and_indirect_freekicks_order','corners_and_indirect_freekicks_text','direct_freekicks_order','direct_freekicks_text','penalties_order','penalties_text','now_cost_rank','now_cost_rank_type','form_rank','form_rank_type','points_per_game_rank','points_per_game_rank_type','selected_rank','selected_rank_type','dreamteam_count','news','news_added','photo','first_name','second_name']
fixtures_unused_columns = ['id', 'code', 'finished', 'finished_provisional', 'minutes', 'provisional_start_time', 'started', 'stats', 'pulse_id']

# %%
url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
r = requests.get(url)
json1 = r.json()

# %%
url_fixtures_df_df = 'https://fantasy.premierleague.com/api/fixtures/'
r2 = requests.get(url_fixtures_df_df)
json2 = r2.json()

# %%
# Set data frames
player_types_df = pd.DataFrame(json1['element_types'])
teams_df = pd.DataFrame(json1['teams'])
events_df = pd.DataFrame(json1['events'])
CURR_GW = events_df.loc[events_df['is_current'] == True]['id'].iloc[-1]
# print(CURR_GW)

# %%
# User team picks
url = f"https://fantasy.premierleague.com/api/entry/{team_id}/event/{CURR_GW}/picks/"
response = requests.get(url)
data = response.json()
picks = data.get("picks", [])
picks_df = pd.DataFrame(picks)
picks_df.to_csv('data/picks.csv')
picks_df = picks_df['element'].to_list()

# %%
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
    
# Classic Leagues
classic_df = pd.json_normalize(data['leagues']['classic'])
classic_df = classic_df[['name','entry_rank','entry_last_rank','entry_percentile_rank']]
classic_league_table = tabulate(classic_df,showindex=False,headers=["Name","Current Rank","Last Rank","Rank percentile"],tablefmt='fancy_grid')

# %%
"""
Fixtures DF
"""

# %%
# Drop & rename columns
fixtures_df = pd.DataFrame(json2)
fixtures_df.drop(fixtures_unused_columns, axis=1, inplace=True)
fixtures_df.rename(columns={'event': 'Gameweek'}, inplace=True)
fixtures_df.head()

# format kick off times
fixtures_df['kickoff_date'] = fixtures_df['kickoff_time'].apply(lambda x: x.split('T')[0])
fixtures_df['kickoff_time'] = fixtures_df['kickoff_time'].apply(lambda x: x.split('T')[1].replace('Z', ''))
fixtures_df = fixtures_df[['Gameweek', 'kickoff_date', 'kickoff_time', 'team_a', 'team_a_score', 'team_h', 'team_h_score', 'team_h_difficulty', 'team_a_difficulty']]

# set team names instead of IDs
fixtures_df['team_a'] = fixtures_df['team_a'].map(teams_df.set_index('id').name)
fixtures_df['team_h'] = fixtures_df['team_h'].map(teams_df.set_index('id').name)

# save 
fixtures_df.to_csv('data/fixtures_list.csv', index=False)

# %%
"""
Get fixtures
"""

# %%
def fixtures_by_team(fixtures, team, gameweek):
    away = fixtures.loc[fixtures['team_a'] == team]
    away.drop(['team_h_difficulty'], axis=1, inplace=True)
    away.rename(columns={'team_a': 'selected_team', 'team_h': 'opponent', 'team_a_difficulty': 'FDR', 'team_a_score': 'selected_team_score', 'team_h_score': 'opponent_score'}, inplace=True)
    away['h_or_a'] = 'Away'
    home = fixtures.loc[fixtures['team_h'] == team]
    home.drop(['team_a_difficulty'], axis=1, inplace=True)
    home.rename(columns={'team_h': 'selected_team', 'team_a': 'opponent', 'team_h_difficulty': 'FDR', 'team_h_score': 'selected_team_score',  'team_a_score': 'opponent_score'}, inplace=True)
    home['h_or_a'] = 'Home'
    combined = pd.concat([away, home])
    return combined.loc[combined['Gameweek'] <= gameweek].sort_values(by='Gameweek')

# %%
"""
Players DF
"""

# %%
players_df = pd.DataFrame(json1['elements'])
# Drop unused columns
players_df = players_df.drop(columns = players_unused_columns)
# Replace position ID with name
players_df['position'] = players_df.element_type.map(player_types_df.set_index('id').singular_name)
# Replace team ID with name
players_df['team'] = players_df.team.map(teams_df.set_index('id').name)
# Create new stats
players_df['element_type'] = players_df['element_type'].replace([1,2,3,4],['GKP','DEF','MID','FWD'])
players_df['now_cost'] = players_df['now_cost']/10
players_df['goal_involvements'] = players_df['goals_scored'] + players_df['assists']
players_df = players_df.astype({"form": float, "total_points": int, "expected_goal_involvements": float, "goal_involvements": float})
players_df['performance'] = players_df['goal_involvements'] - players_df['expected_goal_involvements']
#
fixtures_going_forward = fixtures_df.loc[fixtures_df['Gameweek'] > CURR_GW]
#
players_df['next_match'] = players_df['team'].apply(lambda x: list(fixtures_by_team(fixtures_df, x, CURR_GW+1)[['opponent', 'h_or_a']].iloc[-1]))
players_df['next_3_FDRs'] = players_df['team'].apply(lambda x: list(fixtures_by_team(fixtures_going_forward, x, CURR_GW+3)['FDR']))
players_df['next_3_avg_FDRs'] = players_df['next_3_FDRs'].apply(lambda x: np.round(np.mean(x), 2))
players_df['next_5_FDRs'] = players_df['team'].apply(lambda x: list(fixtures_by_team(fixtures_going_forward, x, CURR_GW+5)['FDR']))
players_df['next_5_avg_FDRs'] = players_df['next_5_FDRs'].apply(lambda x: np.round(np.mean(x), 2))
#
players_df['next_3'] = players_df['team'].apply(lambda x: list(fixtures_by_team(fixtures_going_forward, x, CURR_GW+3)['opponent']))
players_df['next_5'] = players_df['team'].apply(lambda x: list(fixtures_by_team(fixtures_going_forward, x, CURR_GW+5)['opponent']))
players_df = players_df.astype({"next_3": str, "next_5": str, "next_3_avg_FDRs": float, "next_5_avg_FDRs": float})
players_df.to_csv('data/players_data.csv', index=False)

# %%
"""
User team Analysis
"""

# %%
df_my_team = players_df[players_df.id.isin(picks_df)]
# df_my_team = df_my_team.reset_index(drop=True, inplace=True)

df_my_team = df_my_team[['web_name','element_type','now_cost','selected_by_percent','total_points','points_per_game','form','goals_scored','expected_goals','assists','expected_assists','expected_goal_involvements','goal_involvements','ep_next','clean_sheets','bonus','next_3','next_3_avg_FDRs','next_5','next_5_avg_FDRs']]
table_my_team = tabulate(df_my_team,showindex=False,headers=["Name",'Position','Price','selected by(%)','Total points', "PPG",'Form','goals','xG','asists','xA','Expected GI','Delivered GI','Next GW xP','clean sheets','total bonus','next_3', 'next_3_avg_FDRs', 'next_5', 'next_5_avg_FDRs'],tablefmt='fancy_grid')


# %%
"""
Planner
"""

# %%
planner_headers = ['Name','Position','Price','PPG','form','Goal involvements','Next 3','Next 3 Avg FDR','Next 5','Next 5 avg FDR']
df_planner = df_my_team[['web_name','element_type','now_cost','points_per_game','form','goal_involvements','next_3','next_3_avg_FDRs','next_5','next_5_avg_FDRs' ]]
table_team_planner = tabulate(df_planner,showindex=False,headers=planner_headers,tablefmt='fancy_grid')

# %%
"""
watchlist
"""

# %%
# Watchlist
df_watchlist=players_df[~players_df.id.isin(picks_df)]
df_watchlist = df_watchlist[['web_name','element_type','now_cost','selected_by_percent','total_points','points_per_game','form','goals_scored','expected_goals','assists','expected_assists','expected_goal_involvements','goal_involvements','ep_next','clean_sheets','bonus','ict_index_rank','next_3','next_3_FDRs','next_3_avg_FDRs','next_5','next_5_FDRs','next_5_avg_FDRs','team']]

# %%
"""
XGI
"""

# %%
df_watchlist_xgi = df_watchlist.sort_values('expected_goal_involvements',ascending=False).head(10)
df_watchlist_xgi = df_watchlist_xgi[['web_name','element_type','now_cost','selected_by_percent','total_points','goals_scored','expected_goals','assists','expected_assists','expected_goal_involvements','goal_involvements']]
table_xgi_headers = ["Name",'Position','Price','selected by(%)','total points','goals','xG','asists','xA','Expected GI','Delivered GI']
table_xgi = tabulate(df_watchlist_xgi,showindex=False,headers=table_xgi_headers,tablefmt='fancy_grid')
df_watchlist_xgi_names = df_watchlist_xgi['web_name']

# %%
"""
Form
"""

# %%
df_watchlist_form = df_watchlist.sort_values('form',ascending=False).head(10)
table_form_headers = ["Name",'Position','Price','selected by(%)','total points','form','goals','asists','Delivered GI']
df_watchlist_form = df_watchlist_form[['web_name','element_type','now_cost','selected_by_percent','total_points','form','goals_scored','assists','goal_involvements']]
table_form = tabulate(df_watchlist_form,showindex=False,headers=table_form_headers,tablefmt='fancy_grid')
df_watchlist_form_names = df_watchlist_form['web_name']

# %%
"""
Points per Game
"""

# %%
df_watchlist_ppg = df_watchlist.sort_values('points_per_game',ascending=False).head(10)
table_ppg_headers = ["Name",'Position','Price','selected by(%)','total points', "PPG",'goals','asists','Delivered GI']
df_watchlist_ppg = df_watchlist_ppg[['web_name','element_type','now_cost','selected_by_percent','total_points','points_per_game','goals_scored','assists','goal_involvements']]
table_ppg = tabulate(df_watchlist_ppg,showindex=False,headers=table_ppg_headers,tablefmt='fancy_grid')
df_watchlist_ppg_names = df_watchlist_ppg['web_name']

# %%
"""
ICT
"""

# %%
df_watchlist_ict = df_watchlist.sort_values('ict_index_rank',ascending=True).head(10)
table_ict_headers = ["Name",'Position','Price','selected by(%)','total points','goals','xG','asists','xA','Expected GI','Delivered GI','total bonus','ICT Rank']
df_watchlist_ict = df_watchlist_ict[['web_name','element_type','now_cost','selected_by_percent','total_points','goals_scored','expected_goals','assists','expected_assists','expected_goal_involvements','goal_involvements','bonus','ict_index_rank']]   
table_ict = tabulate(df_watchlist_ict,showindex=False,headers=table_ict_headers,tablefmt='fancy_grid')
df_watchlist_ict_names = df_watchlist_ict['web_name']

# %%
"""
xP
"""

# %%
df_watchlist_next_ep = df_watchlist.sort_values('ep_next',ascending=False).head(10)
table_next_ep_headers = ["Name",'Position','Price','selected by(%)','total points','Next GW xP','goals','xG','asists','xA','Expected GI','Delivered GI']
df_watchlist_next_ep = df_watchlist_next_ep[['web_name','element_type','now_cost','selected_by_percent','total_points','ep_next','goals_scored','expected_goals','assists','expected_assists','expected_goal_involvements','goal_involvements']]
table_next_ep = tabulate(df_watchlist_next_ep,showindex=False,headers=table_next_ep_headers,tablefmt='fancy_grid')

# %%
"""
FDR-3
"""

# %%
df_watchlist_fdr3 = df_watchlist.sort_values('next_3_avg_FDRs',ascending=True)
df_watchlist_fdr3 = df_watchlist_fdr3[['team','next_3','next_3_FDRs','next_3_avg_FDRs']]
df_watchlist_fdr3 = df_watchlist_fdr3.drop_duplicates(subset=['team']).head(10)
df_watchlist_fdr3_headers = ["team",'next_3',"next_3_FDRs","next_3_avg_FDRs"]
table_fdr3 = tabulate(df_watchlist_fdr3,showindex=False,headers=df_watchlist_fdr3_headers,tablefmt='fancy_grid')

# %%
"""
Watchlist stats
"""

# %%
df_watchlist_names = pd.concat([df_watchlist_xgi_names,df_watchlist_ppg_names,df_watchlist_form_names,df_watchlist_ict_names])
df_watchlist_names = df_watchlist_names.unique()
df_watchlist_stats = players_df[players_df.web_name.isin(df_watchlist_names)]
#table
df_watchlist_table = df_watchlist_stats[['web_name','team','position','now_cost','expected_goal_involvements','form','points_per_game','ict_index_rank','next_3_avg_FDRs','next_5_avg_FDRs']]
table_watchlist_headers = ["Name","team","position","cost","xGI","form","PPG","ICT Rank","Next-3 FDR (avg)","Next-5 FDR (avg)"]
table_watchlist = tabulate(df_watchlist_table, showindex=False,tablefmt='fancy_grid',headers=table_watchlist_headers)

# %%
"""
TXT file
"""

# %%
with open("results/Team_analysis_watchlist.txt", "w") as f:

        f.write("Player Name :"+player_name)
        f.write("\n")
        f.write("Team Name: "+team_name)
        f.write("\n")
        f.write("Overall Points :"+str(overall_points))
        f.write("\n")
        f.write("Overall Rank :"+str(overall_rank))
        f.write("\n")
        current_gw = CURR_GW
        next_gw = CURR_GW + 1
        f.write("Current GW :"+str(current_gw))
        f.write("\n")
        f.write("Next :" +str(next_gw))
        f.write("\n")


        f.write("\n+++++++++++++++++++++\n")
        f.write("Your team Performance:\n")
        f.write("+++++++++++++++++++++++\n")
        f.write(table_my_team)
        f.write("\n")

        f.write("\n++++++++++++++++++++++++\n")
        f.write("Mini-Leagues performance:\n")
        f.write("++++++++++++++++++++++++\n")
        f.write(classic_league_table)
        f.write("\n")

        f.write("\n+++++++++++++++++++++++++++++++++++++++++++\n")
        f.write("Watchlist (Multi-factor):\n")
        f.write("+++++++++++++++++++++++++++++++++++++++++++\n")
        f.write(table_watchlist)

        f.write("\n+++++++++++++++++++++\n")
        f.write("Watchlist (Best XGI):\n")
        f.write("+++++++++++++++++++++\n")
        f.write(table_xgi)
        f.write("\n")

        f.write("\n++++++++++++++++++++++\n")
        f.write("Watchlist (Best Form):\n")
        f.write("++++++++++++++++++++++\n")
        f.write(table_form)
        f.write("\n")

        f.write("\n++++++++++++++++++++++\n")
        f.write("Next GW Expected Points\n")
        f.write("++++++++++++++++++++++\n")
        f.write(table_next_ep)
        f.write("\n")

        f.write("\n+++++++++++++++++++++++++++++++\n")
        f.write("Watchlist (Top Points per Game):\n")
        f.write("+++++++++++++++++++++++++++++++\n")
        f.write(table_ppg)
        f.write("\n")

        f.write("\n+++++++++++++++++++++++++++++++++++++++++++\n")
        f.write("Watchlist (Top Influence+Creativity+Threat):\n")
        f.write("+++++++++++++++++++++++++++++++++++++++++++\n")
        f.write(table_ict)
        
        
        f.write("\n")
        f.close()

# %%
"""
plotly
"""

# %%
# # XGI
# fig = px.bar(df_watchlist_xgi, x='web_name', y='expected_goal_involvements',color='expected_goal_involvements')
# fig.show()
# # FORM
# fig = px.bar(df_watchlist_form, x='web_name', y='form',color='form')
# fig.show()
# # PPG
# fig = px.bar(df_watchlist_ppg, x='web_name', y='points_per_game',color='points_per_game')
# fig.show()
# # ICT
# fig = px.bar(df_watchlist_ict, x='web_name', y='ict_index_rank',color='ict_index_rank')
# fig.show()
# # FDR-3
# fig = px.bar(df_watchlist_fdr3, x='team', y='next_3_avg_FDRs',color='next_3_avg_FDRs')
# fig.show()
# # FDR-5

# %%
# fig = go.Figure(
#     data=[
#         go.Bar(x=df_watchlist_stats.web_name, y=df_watchlist_stats.expected_goal_involvements,text=df_watchlist_stats.expected_goal_involvements, name="xGI",textposition='auto'),
#         go.Bar(x=df_watchlist_stats.web_name, y=df_watchlist_stats.form,text=df_watchlist_stats.form, name="Form",textposition='auto'),
#         go.Bar(x=df_watchlist_stats.web_name, y=df_watchlist_stats.points_per_game,text=df_watchlist_stats.points_per_game, name="PPG",textposition='auto'),
#         go.Bar(x=df_watchlist_stats.web_name, y=df_watchlist_stats.next_3_avg_FDRs,text=df_watchlist_stats.next_3_avg_FDRs, name="Next 3 Avg FDR",textposition='auto'),
#         go.Bar(x=df_watchlist_stats.web_name, y=df_watchlist_stats.next_5_avg_FDRs,text=df_watchlist_stats.next_5_avg_FDRs, name="Next 5 Avg FDR",textposition='auto'),
#     ],
#     layout=dict(
#         barcornerradius=15,
#     ),
# )

# fig.update_layout(
#     autosize=False,
#     width=1800,
#     height=800,
# )
# fig.show()
