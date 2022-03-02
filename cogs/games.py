from discord.commands import slash_command
from discord.ext import commands
from discord import Option
import discord
import time
import nba

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    """
    Returns NBA games on a specified date (defaults to the current day if none is provided).
    Example:
    New Orleans Pelicans at Phoenix Suns
    __Final__
    **NOP**: 117 **WIN**
    **PHX**: 102
    """
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

        for game in nba.get_games(start_date=f"{year}-{month}-{day}", end_date=f"{year}-{month}-{day}", per_page=100)["data"]:
            title = f"{game['visitor_team']['full_name']} at {game['home_team']['full_name']}"
            body = f"**{game['visitor_team']['abbreviation']}**: {game['visitor_team_score']} **{game['home_team']['abbreviation']}**: {game['home_team_score']}"

            if game["status"] == "Final":
                if game['visitor_team_score'] > game['home_team_score']:
                    body += f" *{game['visitor_team']['name']} WIN*"
                
                elif game['home_team_score'] > game['visitor_team_score']:
                    body += f" *{game['home_team']['name']} WIN*"

            if game['status'] != "Final":
                body += "\n{} {}".format(game['status'], f"({game['time']})" if len(game['time']) > 0 else "")

            embed.add_field(name=title, value=body, inline=False)

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.respond(embed=embed)

"""
Registers command when the cog is setup.
"""
def setup(bot):
    bot.add_cog(Games(bot))