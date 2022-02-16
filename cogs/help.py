from discord.commands import slash_command
from discord.ext import commands
import discord

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @slash_command(name="help", description="Lists NBA bot commands")
    async def help(self, ctx):
        embed = discord.Embed(title="NBA Bot Commands", color=self.bot.embed_color)
        embed.set_thumbnail(url=self.bot.thumbnail_link)

        embed.add_field(name="/games", value="Lists NBA games that are playing today", inline=True)
        embed.add_field(name="/standings", value="Lists NBA teams ranked by winning percentage", inline=True)
        embed.add_field(name="/team <team name>", value="Lists stats on a particular NBA team", inline=True)

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))