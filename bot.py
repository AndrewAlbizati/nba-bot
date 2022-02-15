import discord
from discord import Option
from discord.ext import commands
import asyncio
import requests
import random
import json
import time

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
            data = json.load(f)
        
        for key in data:
            self.team_win_loss[int(key)] = self.get_win_loss(int(key))

        

        @self.slash_command(name="games",description="Lists NBA games that are playing today")
        async def games(ctx):
            t = time.localtime()

            embed = discord.Embed(title = "NBA Games Today", color = self.embed_color)
            embed.set_thumbnail(url=self.thumbnail_link)

            for game in self.get_games(t[0], t[1], t[2]):
                title = f"{game['visitor_team']['full_name']} at {game['home_team']['full_name']}"
                body = f"{game['status']} ({game['visitor_team_score']} - {game['home_team_score']})"

                if game["status"].lower() == "final":
                    if game['visitor_team_score'] > game['home_team_score']:
                        body += f" **{game['visitor_team']['name'].upper()} WIN**"
                    else:
                        body += f" **{game['home_team']['name'].upper()} WIN**"

                body += f"\n**{game['visitor_team']['abbreviation']}**: ({self.team_win_loss[int(game['visitor_team']['id'])][0]} - {self.team_win_loss[int(game['visitor_team']['id'])][1]})"
                body += f"\n**{game['home_team']['abbreviation']}**: ({self.team_win_loss[int(game['home_team']['id'])][0]} - {self.team_win_loss[int(game['home_team']['id'])][1]})"
                
                embed.add_field(name=title, value=body, inline=False)

            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
            await ctx.respond(embed=embed)



        @self.slash_command(name="standings",description="Lists NBA teams ranked by winning percentage")
        async def standings(ctx):
            embed = discord.Embed(title = "NBA Teams", color = self.embed_color)
            embed.set_thumbnail(url=self.thumbnail_link)
            
            with open("teams.json", "r") as f:
                data = json.load(f)
            
            eastern_team_percentages = {}
            western_team_percentages = {}

            for key in self.team_win_loss:
                if data[str(key)]["conference"] == "East":
                    eastern_team_percentages[key] = round(self.team_win_loss[key][0] / (self.team_win_loss[key][0] + self.team_win_loss[key][1]), 3)
                else:
                    western_team_percentages[key] = round(self.team_win_loss[key][0] / (self.team_win_loss[key][0] + self.team_win_loss[key][1]), 3)
            
            eastern_body = ""
            for i, key in enumerate(dict(reversed(sorted(eastern_team_percentages.items(), key=lambda item: item[1])))):
                if i < 6:
                    eastern_body += "**"
                elif i >= 6 and i <= 9:
                    eastern_body += "*"

                eastern_body += f"{i + 1}. {data[str(key)]['full_name']}"

                if i < 6:
                    eastern_body += "**"
                elif i >= 6 and i <= 9:
                    eastern_body += "*"

                eastern_body += f" ({eastern_team_percentages[key]})\n"

                if i == 9:
                    eastern_body += "-------------------------------\n"
            
            western_body = ""
            for i, key in enumerate(dict(reversed(sorted(western_team_percentages.items(), key=lambda item: item[1])))):
                if i < 6:
                    western_body += "**"
                elif i >= 6 and i <= 9:
                    western_body += "*"

                western_body += f"{i + 1}. {data[str(key)]['full_name']}"

                if i < 6:
                    western_body += "**"
                elif i >= 6 and i <= 9:
                    western_body += "*"

                western_body += f" ({western_team_percentages[key]})\n"

                if i == 9:
                    western_body += "-------------------------------\n"

            embed.add_field(name="Eastern Conference", value=eastern_body)
            embed.add_field(name="Western Conference", value=western_body)

            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
            await ctx.respond(embed=embed)
        


        @self.slash_command(name="team",description="Get stats on a particular NBA team")
        async def team(ctx, name: Option(str, "NBA team name", autocomplete=self.get_autocompleted_team_names)):
            with open("teams.json", "r") as f:
                data = json.load(f)
            
            team_id = 0
            for key in data:
                if data[key]["full_name"].lower() == name.lower() or data[key]["name"].lower() == name.lower():
                    name = data[key]["full_name"]
                    team_id = int(key)
            
            if team_id == 0:
                await ctx.respond("Please pick a valid NBA team!", ephemeral=True)
                return
            
            embed = discord.Embed(title=name)
            embed.color = discord.Color.from_rgb(data[str(team_id)]["color"][0], data[str(team_id)]["color"][1], data[str(team_id)]["color"][2])
            embed.set_thumbnail(url=data[str(team_id)]["logo"])

            await ctx.respond(embed=embed)
    
    async def get_autocompleted_team_names(self, ctx):
        names = ["Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets", "Chicago Bulls", "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets", "Detroit Pistons", "Golden State Warrios", "Houston Rockets", "Indiana Pacers", "Los Angeles Clippers", "Los Angeles Lakers", "Memphis Grizzlies", "Miami Heat", "Milwaukee", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks", "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns", "Portland Trail Blazers", "Sacramento Kings", "Toronto Raptors", "Utah Jazz", "Washington Wizards"]
        return [name for name in names if ctx.value.lower() in name.lower()]
    
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