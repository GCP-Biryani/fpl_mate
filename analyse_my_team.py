import requests
import pandas as pd
from tabulate import tabulate
from datetime import datetime, timezone

# Input team ID
team_id = input("Enter your FPL ID:")

# base URL
BASE_URL = 'https://fantasy.premierleague.com/api/'

#=====================================
# Player specific data
def get_player_history(player_id, elements = 'history'):
    '''get all gameweek info for a given player_id'''
    req_json = requests.get(BASE_URL + 'element-summary/' + str(player_id) + '/').json()
    return pd.json_normalize(req_json[elements])
#=====================================
# Fixtures data
def get_fixture_data():
    '''get all gameweek info for a given player_id'''
    req_json = requests.get(BASE_URL + 'fixtures/').json()
    fixtures_df = pd.json_normalize(req_json)
    return fixtures_df
#=====================================
# Current gameweek
def get_current_gw():
    # print('Fetching curr gameweek...')
    URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
    DATA = requests.get(URL).json()
    CURR_GW_OBJS = [x for x in DATA['events'] if x['is_current'] == True]
    if len(CURR_GW_OBJS) == 0:
        CURR_GW_OBJS = DATA['events']        
    CURR_GW = CURR_GW_OBJS[-1]['id']
    return CURR_GW
#=====================================
# Get next GW deadline
def get_next_gw():
    URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
    DATA = requests.get(URL).json()
    current_gw = get_current_gw()
    next_gw = current_gw
    NEXT_GW_NAME = DATA['events'][next_gw]['name']
    NEXT_GW = str(NEXT_GW_NAME)
    return NEXT_GW
#=====================================
# user team
def get_team(team_id):
    gw = get_current_gw()
    url = f"https://fantasy.premierleague.com/api/entry/{team_id}/event/{gw}/picks/"

    # Send a GET request to fetch the data
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # # Save the new JSON response to the file
        # with open('team.json', "w") as json_file:
        #     json.dump(data, json_file, indent=2)
    # print(f"Data for team {team_id} in GW {gw} successfully saved")
    picks = data.get("picks", [])
    picks_df = pd.DataFrame(picks)
    picks_df = picks_df['element'].to_list()
    # print (picks_df)
    return picks_df
#=====================================
# Teams
def get_global_info(elements = 'teams'):
    '''get all team data'''
    req_json = requests.get(BASE_URL + 'bootstrap-static/').json()
    return pd.json_normalize(req_json[elements])
#=====================================
# Get user team details
def get_my_team(team_id):
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
    
    # Full elements
    full_elements_df = get_global_info('elements')
    elements_columns_to_drop = ['chance_of_playing_next_round','chance_of_playing_this_round','code','cost_change_event','cost_change_event_fall','cost_change_start','cost_change_start_fall','in_dreamteam','special','squad_number','transfers_in','transfers_in_event','transfers_out','transfers_out_event','region','influence_rank_type','creativity_rank_type','threat_rank_type','ict_index_rank_type','corners_and_indirect_freekicks_order','corners_and_indirect_freekicks_text','direct_freekicks_order','direct_freekicks_text','penalties_order','penalties_text','now_cost_rank','now_cost_rank_type','form_rank','form_rank_type','points_per_game_rank','points_per_game_rank_type','selected_rank','selected_rank_type','dreamteam_count','news','news_added','photo','first_name','second_name']
    full_elements_df.drop(columns=elements_columns_to_drop,inplace=True)
    full_elements_df['element_type'] = full_elements_df['element_type'].replace([1,2,3,4],['GKP','DEF','MID','FWD'])
    full_elements_df['now_cost'] = full_elements_df['now_cost']/10
    full_elements_df = full_elements_df.astype({"form": float, "total_points": int})
    full_elements_df['goal_involvements'] = full_elements_df['goals_scored'] + full_elements_df['assists']
    full_elements_df = full_elements_df.astype({"expected_goal_involvements": float, "goal_involvements": float})
    full_elements_df['performance'] = full_elements_df['goal_involvements'] - full_elements_df['expected_goal_involvements']
    full_elements_df.to_csv('data/full_elements_df.csv')
    my_team = get_team(team_id)
    full_elements_df = pd.read_csv('data/full_elements_df.csv')
    df_my_team=full_elements_df[full_elements_df.id.isin(my_team)]
    df_my_team.reset_index(drop=True, inplace=True)
    tabulate_headers = ["Name",'Position','Price','selected by(%)','total points', "PPG",'form','goals','xG','asists','xA','Expected GI','Delivered GI','Next GW xP','clean sheets','total bonus','ICT rank']
    df_my_team = df_my_team[['web_name','element_type','now_cost','selected_by_percent','total_points','points_per_game','form','goals_scored','expected_goals','assists','expected_assists','expected_goal_involvements','goal_involvements','ep_next','clean_sheets','bonus']]
    table_my_team = tabulate(df_my_team,showindex=False,headers=["Name",'Position','Price','selected by(%)','Total points', "PPG",'Form','goals','xG','asists','xA','Expected GI','Delivered GI','Next GW xP','clean sheets','total bonus'],tablefmt='fancy_grid')
    
    df_watchlist=full_elements_df[~full_elements_df.id.isin(my_team)]
    df_watchlist = df_watchlist[['web_name','element_type','now_cost','selected_by_percent','total_points','points_per_game','form','goals_scored','expected_goals','assists','expected_assists','expected_goal_involvements','goal_involvements','ep_next','clean_sheets','bonus','ict_index_rank']]
    #
    df_watchlist_xgi = df_watchlist.sort_values('expected_goal_involvements',ascending=False).head(10)
    table_xfi = tabulate(df_watchlist_xgi,showindex=False,headers=tabulate_headers,tablefmt='fancy_grid')
    #
    df_watchlist_form = df_watchlist.sort_values('form',ascending=False).head(10)
    table_form = tabulate(df_watchlist_form,showindex=False,headers=tabulate_headers,tablefmt='fancy_grid')
    #
    df_watchlist_ppg = df_watchlist.sort_values('points_per_game',ascending=False).head(10)
    table_ppg = tabulate(df_watchlist_ppg,showindex=False,headers=tabulate_headers,tablefmt='fancy_grid')
    #
    df_watchlist_ict = df_watchlist.sort_values('ict_index_rank',ascending=True).head(10)
    table_ict = tabulate(df_watchlist_ict,showindex=False,headers=tabulate_headers,tablefmt='fancy_grid')
    #
    df_watchlist_next_ep = df_watchlist.sort_values('ep_next',ascending=False).head(10)
    table_next_ep = tabulate(df_watchlist_next_ep,showindex=False,headers=tabulate_headers,tablefmt='fancy_grid')
    


    with open("data/Team_analysis_watchlist.txt", "w") as f:

        f.write("Player Name :"+player_name)
        f.write("\n")
        f.write("Team Name: "+team_name)
        f.write("\n")
        f.write("Overall Points :"+str(overall_points))
        f.write("\n")
        f.write("Overall Rank :"+str(overall_rank))
        f.write("\n")
        current_gw = get_current_gw()
        next_gw = get_next_gw()
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

        f.write("\n+++++++++++++++++++++\n")
        f.write("Watchlist (Best XGI):\n")
        f.write("+++++++++++++++++++++\n")
        f.write(table_xfi)
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
#=====================================
# Form

#=====================================
# XGI
#=====================================
#EP_NEXT
#=====================================

get_my_team(team_id)