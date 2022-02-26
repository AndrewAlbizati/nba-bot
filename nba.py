import time
import requests

MAIN_URL = "https://www.balldontlie.io/api/v1"

def make_request(url):
    r = requests.get(url)

    return r.json()

def search_player(search, page=0, per_page=25):
    url = f"{MAIN_URL}/players?"

    url += f"page={page}"
    url += f"&per_page={per_page}"

    url += f"&search={search}"

    return make_request(url)

def get_player(id):
    url = f"{MAIN_URL}/players/{id}"

    return make_request(url)

def get_all_teams(page=0, per_page=30):
    url = f"{MAIN_URL}/teams?"
    
    url += f"page={page}"
    url += f"&per_page={per_page}"

    return make_request(url)

def get_team(id):
    url = f"{MAIN_URL}/teams/{id}"

    return make_request(url)

def get_games(page=0, per_page=25, dates=None, seasons=None, team_ids=None, postseason=None, start_date=None, end_date=None):
    url = f"{MAIN_URL}/games?"

    url += f"page={page}"
    url += f"&per_page={per_page}"

    if dates != None:
        for date in dates:
            url += f"&dates[]={date}"
    
    if seasons != None:
        for season in seasons:
            url += f"&seasons[]={season}"
    
    if team_ids != None:
        for team_id in team_ids:
            url += f"&team_ids[]={team_id}"

    if postseason != None:
        url += f"&postseason={str(postseason)}"
    
    if start_date != None:
        url += f"&start_date={start_date}"
    
    if end_date != None:
        url += f"&end_date={end_date}"

    return make_request(url)

def get_game(id):
    url = f"{MAIN_URL}/games/{id}"

    return make_request(url)

def get_stats(page=0, per_page=25, dates=None, seasons=None, player_ids=None, game_ids=None, postseason=None, start_date=None, end_date=None):
    url = f"{MAIN_URL}/stats?"

    url += f"page={page}"
    url += f"&per_page={per_page}"

    if dates != None:
        for date in dates:
            url += f"&dates[]={date}"
    
    if seasons != None:
        for season in seasons:
            url += f"&seasons[]={season}"
    
    if player_ids != None:
        for player_id in player_ids:
            url += f"&player_ids[]={player_id}"

    if game_ids != None:
        for game_id in game_ids:
            url += f"&game_ids[]={game_id}"

    if postseason != None:
        url += f"&postseason={str(postseason)}"
    
    if start_date != None:
        url += f"&start_date={start_date}"
    
    if end_date != None:
        url += f"&end_date={end_date}"

    return make_request(url)

def get_season_averages(season=None, player_ids=None):
    url = "https://www.balldontlie.io/api/v1/season_averages?"

    if season == None:
        season = time.localtime()[0]
    url += f"season={season}"

    if player_ids != None:
        for player_id in player_ids:
            url += f"&player_ids[]={player_id}"

    return make_request(url)