import discord # pip install py-cord==2.0.0b3
from discord.ext import commands
import json
import requests
import time

class Bot():
    embed_color = 0x22529a

    season_start_year = 2021
    season_start_month = 10
    season_start_day = 19

    team_win_loss = {}

    def __init__(self):
        try:
            f = open("config.json", "x") # Raises FileExistsError if already present
            data = {}
            data["discord-bot-token"] = "{PASTE TOKEN INSIDE QUOTATION MARKS}"

            json.dump(data, f, indent=4)
            f.close()
            
            raise ValueError("Please provide necessary tokens in config.json")
        except FileExistsError:
            pass

        # Get token from config.json
        with open("config.json", "r") as f:
            data = json.load(f)
        
        self.TOKEN = data["discord-bot-token"]
        self.bot = commands.Bot()
        self.bot.remove_command("help")

        with open("teams.json", "r") as f:
            data = json.load(f)

            for key in data:
                self.team_win_loss[int(key)] = self.get_win_loss(int(key))


        @self.bot.event
        async def on_ready():
            print(f'{self.bot.user} has connected to Discord!')

        @self.bot.slash_command(description="Returns a list of NBA games that are playing")
        async def games(ctx):
            start = time.time()
            t = time.localtime()

            embed = discord.Embed(title = "NBA Games Today", color = self.embed_color)
            embed.set_thumbnail(url="https://theprodigious.com/wp-content/uploads/2021/09/nba-logo.jpg")

            for game in self.get_games(t[0], t[1], t[2]):
                title = f"{game['visitor_team']['full_name']} at {game['home_team']['full_name']}"
                body = f"{game['status']} ({game['visitor_team_score']} - {game['home_team_score']})"

                if game["status"].lower() == "final":
                    if game['visitor_team_score'] > game['home_team_score']:
                        body += f" **{game['visitor_team']['name'].upper()} WIN**"
                    else:
                        body += f" **{game['home_team']['name'].upper()} WIN**"
                
                embed.add_field(name=title, value=body, inline=False)

            embed.set_footer(text=f"Requested by {ctx.author} in {int(round((time.time() - start) * 1000, 0))} milliseconds", icon_url=ctx.author.avatar)
            await ctx.respond(embed=embed)


        @self.bot.slash_command(description="Returns a list of NBA teams ranked by winning percentage")
        async def teams(ctx):
            start = time.time()
            embed = discord.Embed(title = "NBA Teams", color = self.embed_color)
            
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

            embed.add_field(name="Eastern Conference", value=eastern_body)
            embed.add_field(name="Western Conference", value=western_body)

            embed.set_footer(text=f"Requested by {ctx.author} in {int(round((time.time() - start) * 1000, 0))} milliseconds", icon_url=ctx.author.avatar)
            await ctx.respond(embed=embed)
    
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

                

    def run(self):
        self.bot.run(self.TOKEN)

if __name__ == "__main__":
    bot = Bot()
    bot.run()