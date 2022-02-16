from discord.commands import slash_command
from discord.ext import commands
from discord import Option
import discord

async def get_autocompleted_team_names(ctx):
    names = ["Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets", "Chicago Bulls", "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets", "Detroit Pistons", "Golden State Warriors", "Houston Rockets", "Indiana Pacers", "LA Clippers", "Los Angeles Lakers", "Memphis Grizzlies", "Miami Heat", "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks", "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns", "Portland Trail Blazers", "Sacramento Kings", "Toronto Raptors", "Utah Jazz", "Washington Wizards"]
    return [name for name in names if ctx.value.lower() in name.lower()]

class Team(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="team",description="Lists stats on a particular NBA team")
    async def team(self, ctx, name: Option(str, "NBA team name", autocomplete=get_autocompleted_team_names)):    
        team_id = 0
        for key in self.bot.team_data:
            if self.bot.team_data[key]["full_name"].lower() == name.lower() or self.bot.team_data[key]["name"].lower() == name.lower():
                name = self.bot.team_data[key]["full_name"]
                team_id = int(key)
        
        if team_id == 0:
            await ctx.respond("Please pick a valid NBA team!", ephemeral=True)
            return
        
        embed = discord.Embed(title=f"{name} ({self.bot.team_data[str(team_id)]['abbreviation']})")
        embed.color = discord.Color.from_rgb(self.bot.team_data[str(team_id)]["color"][0], self.bot.team_data[str(team_id)]["color"][1], self.bot.team_data[str(team_id)]["color"][2])
        embed.set_thumbnail(url=self.bot.team_data[str(team_id)]["logo"])

        win_loss = self.bot.get_win_loss(team_id)

        conference_percentages = {}

        for key in self.bot.team_win_loss:
            if self.bot.team_data[str(key)]["conference"] == self.bot.team_data[str(team_id)]["conference"]:
                conference_percentages[key] = round(self.bot.team_win_loss[key][0] / (self.bot.team_win_loss[key][0] + self.bot.team_win_loss[key][1]), 3)
        
        rank = 1
        for key in dict(reversed(sorted(conference_percentages.items(), key=lambda item: item[1]))):
            if key != team_id:
                rank += 1
            else:
                break
        
        get_ordinal = lambda n: "%d%s"%(n,{1:"st",2:"nd",3:"rd"}.get(n if n<20 else n%10,"th"))
        rank_in_conference = get_ordinal(rank)

        embed.add_field(name="Win/Loss",value=f"**{win_loss[0]} - {win_loss[1]}** ({round(win_loss[0] / (win_loss[0] + win_loss[1]), 3)})\n*{rank_in_conference.upper()} IN {self.bot.team_data[str(key)]['conference'].upper()}*")

        await ctx.respond(embed=embed)
    

def setup(bot):
    bot.add_cog(Team(bot))