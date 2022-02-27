import discord
from discord.ext import commands
import asyncio
import random
import json
import time
import os
import nba

class Bot(commands.Bot):
    embed_color = 0x1d428a

    season_start_year = 2021
    season_start_month = 10
    season_start_day = 19

    thumbnail_link = "https://theprodigious.com/wp-content/uploads/2021/09/nba-logo.jpg"

    team_win_loss = {}
    games_played_today = []

    """
    Initializes all teams win/loss data, loads cogs.
    """
    def __init__(self):
        super().__init__()
        self.loop.create_task(self.change_status())
        self.loop.create_task(self.update_games())

        with open("teams.json", "r") as f:
            self.team_data = json.load(f)
        
        for key in self.team_data:
            self.team_win_loss[int(key)] = self.get_win_loss(int(key))

        for cog in os.listdir("./cogs"):
            if cog.endswith(".py"):
                self.load_extension(f"cogs.{cog[:-3]}")
                print("Loaded " + cog)

    """
    Changes the bot's status every ten minutes and checks if a game is playing.
    Example status:
    Watching Lakers vs Celtics
    """
    async def change_status(self):
        await self.wait_until_ready()

        while not self.is_closed():
            t = time.localtime()
            games = nba.get_games(start_date=f"{t[0]}-{t[1]}-{t[2]}", end_date=f"{t[0]}-{t[1]}-{t[2]}", per_page=100)["data"]

            active_games = []

            for game in games:
                if game["status"] != "Final" and not "ET" in game["status"]:
                    active_games.append(game)
            
            if len(active_games) == 0:
                await self.change_presence(status=discord.Status.idle)
            
            else:
                game = random.choice(active_games)
                status = f"{game['visitor_team']['name']} vs {game['home_team']['name']}"

                activity = discord.Activity(type=discord.ActivityType.watching, name=status)

                await self.change_presence(status=discord.Status.online, activity=activity)
            await asyncio.sleep(60 * 10) # 10 minutes 

    """
    Updates the win/loss for all teams every minute.
    """
    async def update_games(self):
        await self.wait_until_ready()

        while not self.is_closed():
            try:
                t = time.localtime()
                games = nba.get_games(start_date=f"{t[0]}-{t[1]}-{t[2]}", end_date=f"{t[0]}-{t[1]}-{t[2]}", per_page=100)["data"]

                for game in games:
                    if game["status"] == "Final" and not int(game["id"]) in self.games_played_today:
                        if game["home_team_score"] > game["visitor_team_score"]:
                            winner_id = game["home_team"]["id"]
                            loser_id = game["visitor_team"]["id"]
                        elif game["home_team_score"] < game["visitor_team_score"]:
                            winner_id = game["visitor_team"]["id"]
                            loser_id = game["home_team"]["id"]
                        
                        if winner_id == None or loser_id == None:
                            continue

                        win_loss = list(self.team_win_loss[int(winner_id)])
                        win_loss[0] = win_loss[0] + 1

                        self.team_win_loss[int(winner_id)] = tuple(win_loss)


                        win_loss = list(self.team_win_loss[int(winner_id)])
                        win_loss[1] = win_loss[1] + 1

                        self.team_win_loss[int(loser_id)] = tuple(win_loss)

                        
                        self.games_played_today.append(int(game["id"]))
                
            except Exception as e:
                print(e)

            
            # Reset games played at 12:15 AM
            if t[1] == 0 and t[2] == 15:
                self.games_played_today = []

            await asyncio.sleep(60) # 1 minute

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        
    """
    Gets the win/loss record for a specific team.
    """
    def get_win_loss(self, team_id):
        t = time.localtime()
        page = 0
        nextpage = True

        wins = 0
        losses = 0
        while nextpage:
            r = nba.get_games(seasons=[t[0] - 1], team_ids=[team_id], per_page=100, page=page)

            nextpage = r["meta"]["next_page"] != None
            page += 1

            for game in r["data"]:
                if game["status"].lower() != "final":
                    continue
                    
                date = game["date"].split("-")

                year = int(date[0])
                month = int(date[1])
                day = int(date[2].split("T")[0])

                if year < self.season_start_year:
                    continue

                if year == self.season_start_year:
                    if month < self.season_start_month:
                        continue
                    if month == self.season_start_month and day < self.season_start_day:
                        continue
                
                # Fix incorrect game score
                if game["id"] == 474073:
                    game["home_team_score"] = 101
                    game["visitor_team_score"] = 95
                
                if game["home_team"]["id"] == team_id:
                    if game["home_team_score"] > game["visitor_team_score"]:
                        wins += 1
                    elif game["home_team_score"] < game["visitor_team_score"]:
                        losses += 1
                else:
                    if game["home_team_score"] < game["visitor_team_score"]:
                        wins += 1
                    elif game["home_team_score"] > game["visitor_team_score"]:
                        losses += 1
        
        return (wins, losses)