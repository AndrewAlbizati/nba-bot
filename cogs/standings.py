from discord.commands import slash_command
from discord.ext import commands
import discord

class Standings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """
    Returns the NBA winning standings for all teams seperated by conference.
    Teams that will be guranteed a playoff spot are bolded.
    Teams that will compete in the play-in tournament are italicized.
    """
    @slash_command(name="standings", description="Lists NBA teams ranked by winning percentage")
    async def standings(self, ctx):
        embed = discord.Embed(title="NBA Teams", color=self.bot.embed_color)
        embed.set_thumbnail(url=self.bot.thumbnail_link)
        
        eastern_team_percentages = {}
        western_team_percentages = {}

        for key in self.bot.team_win_loss:
            if self.bot.team_data[str(key)]["conference"] == "East":
                eastern_team_percentages[key] = round(self.bot.team_win_loss[key][0] / (self.bot.team_win_loss[key][0] + self.bot.team_win_loss[key][1]), 3)
            else:
                western_team_percentages[key] = round(self.bot.team_win_loss[key][0] / (self.bot.team_win_loss[key][0] + self.bot.team_win_loss[key][1]), 3)
        
        eastern_body = ""
        for i, key in enumerate(dict(reversed(sorted(eastern_team_percentages.items(), key=lambda item: item[1])))):
            if i < 6:
                eastern_body += "**"
            elif i >= 6 and i <= 9:
                eastern_body += "*"

            eastern_body += f"{i + 1}. {self.bot.team_data[str(key)]['full_name']}"

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

            western_body += f"{i + 1}. {self.bot.team_data[str(key)]['full_name']}"

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

"""
Registers command when the cog is setup.
"""
def setup(bot):
    bot.add_cog(Standings(bot))