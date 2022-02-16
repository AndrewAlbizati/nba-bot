from discord.commands import slash_command
from discord.ext import commands
import discord
import time

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @slash_command(name="games", description="Lists NBA games that are playing today")
    async def games(self, ctx):
        t = time.localtime()

        embed = discord.Embed(title="NBA Games Today", color=self.bot.embed_color)
        embed.set_thumbnail(url=self.bot.thumbnail_link)

        for game in self.bot.get_games(t[0], t[1], t[2]):
            title = f"{game['visitor_team']['full_name']} at {game['home_team']['full_name']}"
            body = f"{game['status']} ({game['visitor_team_score']} - {game['home_team_score']})"

            if game["status"].lower() == "final":
                if game['visitor_team_score'] > game['home_team_score']:
                    body += f" **{game['visitor_team']['name'].upper()} WIN**"
                else:
                    body += f" **{game['home_team']['name'].upper()} WIN**"

            body += f"\n**{game['visitor_team']['abbreviation']}**: ({self.bot.team_win_loss[int(game['visitor_team']['id'])][0]} - {self.bot.team_win_loss[int(game['visitor_team']['id'])][1]})"
            body += f"\n**{game['home_team']['abbreviation']}**: ({self.bot.team_win_loss[int(game['home_team']['id'])][0]} - {self.bot.team_win_loss[int(game['home_team']['id'])][1]})"
            
            embed.add_field(name=title, value=body, inline=False)

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Games(bot))