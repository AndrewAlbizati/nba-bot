from discord.commands import slash_command
from discord.ext import commands
from discord import Option
import discord
import time
import nba

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @slash_command(name="games", description="Lists NBA games that are playing on a certain date")
    async def games(self, ctx, date: Option(str, "Date (YYYY-MM-DD)", required=False)):
        if date != None:
            year = int(date.split("-")[0])
            month = int(date.split("-")[1])
            day = int(date.split("-")[2])
        else:
            t = time.localtime()
            year = t[0]
            month = t[1]
            day = t[2]

        embed = discord.Embed(title=f"NBA Games ({year}-{month}-{day})", color=self.bot.embed_color)
        embed.set_thumbnail(url=self.bot.thumbnail_link)

        for game in nba.get_games(start_date=f"{year}-{month}-{day}", per_page=100)["data"]:
            title = f"{game['visitor_team']['full_name']} at {game['home_team']['full_name']}"
            body = f"{game['status']} ({game['visitor_team_score']} - {game['home_team_score']})"

            if game["status"].lower() == "final":
                if game['visitor_team_score'] > game['home_team_score']:
                    body += f" **{game['visitor_team']['name'].upper()} WIN**"
                else:
                    body += f" **{game['home_team']['name'].upper()} WIN**"


            embed.add_field(name=title, value=body, inline=False)

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Games(bot))