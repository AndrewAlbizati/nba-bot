import discord
from discord.ext import commands
import asyncio
import requests
import random
import json
import time
import os

class Bot(commands.Bot):
    embed_color = 0x1d428a

    season_start_year = 2021
    season_start_month = 10
    season_start_day = 19

    thumbnail_link = "https://theprodigious.com/wp-content/uploads/2021/09/nba-logo.jpg"

    team_win_loss = {}
    games_played_today = []

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

    
    async def change_status(self):
        await self.wait_until_ready()

        while not self.is_closed():
            t = time.localtime()
            games = self.get_games(t[0], t[1], t[2])

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

    async def update_games(self):
        await self.wait_until_ready()

        while not self.is_closed():
            t = time.localtime()
            games = self.get_games(t[0], t[1], t[2])

            for game in games:
                if game["status"] == "Final" and not int(game["id"]) in self.games_played_today:
                    if game["home_team_score"] > game["visitor_team_score"]:
                        winner_id = game["home_team"]["id"]
                        loser_id = game["visitor_team"]["id"]
                    else:
                        winner_id = game["visitor_team"]["id"]
                        loser_id = game["home_team"]["id"]

                    win_loss = list(self.team_win_loss[int(winner_id)])
                    win_loss[0] = win_loss[0] + 1

                    self.team_win_loss[int(winner_id)] = tuple(win_loss)


                    win_loss = list(self.team_win_loss[int(winner_id)])
                    win_loss[1] = win_loss[1] + 1

                    self.team_win_loss[int(loser_id)] = tuple(win_loss)

                    
                    self.games_played_today.append(int(game["id"]))
            
            # Reset games played at 12:15 AM
            if t[1] == 0 and t[2] == 15:
                self.games_played_today = []

            await asyncio.sleep(60) # 1 minute

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        
    
    def get_games(self, year, month, day):
        date = f"{year}-{month}-{day}"
        url = f"https://www.balldontlie.io/api/v1/games/?start_date={date}&end_date={date}"

        r = requests.get(url)

        return r.json()["data"]
    
    def get_win_loss(self, team_id):
        t = time.localtime()
        page = 1
        nextpage = True

        wins = 0
        losses = 0
        while nextpage:
            url = f"https://www.balldontlie.io/api/v1/games/?seasons[]={t[0] - 1}&team_ids[]={team_id}&per_page=100&page={page}"
            r = requests.get(url).json()

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
                
                if game["home_team"]["id"] == team_id:
                    if game["home_team_score"] > game["visitor_team_score"]:
                        wins += 1
                        continue
                else:
                    if game["home_team_score"] < game["visitor_team_score"]:
                        wins += 1
                        continue
                
                losses += 1
        
        return (wins, losses)