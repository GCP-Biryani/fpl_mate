import pandas as pd
import numpy as np
import requests
import streamlit as st

url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
r = requests.get(url)
json1 = r.json()
#
url_fixtures_df_df = 'https://fantasy.premierleague.com/api/fixtures/'
r2 = requests.get(url_fixtures_df_df)
json2 = r2.json()
#
# Set data frames
player_types_df = pd.DataFrame(json1['element_types'])
teams_df = pd.DataFrame(json1['teams'])
events_df = pd.DataFrame(json1['events'])
CURR_GW = events_df.loc[events_df['is_current'] == True]['id'].iloc[-1]
#
st.session_state.gameweek = CURR_GW
#
players_unused_columns = ['chance_of_playing_next_round','chance_of_playing_this_round','code','cost_change_event','cost_change_event_fall','cost_change_start','cost_change_start_fall','in_dreamteam','special','squad_number','transfers_in','transfers_in_event','transfers_out','transfers_out_event','region','influence_rank_type','creativity_rank_type','threat_rank_type','ict_index_rank_type','corners_and_indirect_freekicks_order','corners_and_indirect_freekicks_text','direct_freekicks_order','direct_freekicks_text','penalties_order','penalties_text','now_cost_rank','now_cost_rank_type','form_rank','form_rank_type','points_per_game_rank','points_per_game_rank_type','selected_rank','selected_rank_type','dreamteam_count','news','news_added','photo','first_name','second_name']
fixtures_unused_columns = ['id', 'code', 'finished', 'finished_provisional', 'minutes', 'provisional_start_time', 'started', 'stats', 'pulse_id']
#
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
fixtures_df.to_csv('./fixtures_list.csv', index=False)

#
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

#
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
players_df.to_csv('./players_data.csv', index=False)