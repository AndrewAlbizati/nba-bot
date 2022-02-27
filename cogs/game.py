from tkinter import E
from discord.commands import slash_command
from discord.ext import commands
from discord import Option
import discord
import time
import nba

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def get_games(ctx):
        games = []
        try:
            date = ctx.options["date"]
            if date == None or date == "":
                raise TypeError()
        except TypeError:
            t = time.localtime()
            date = f"{t[0]}-{t[1]}-{t[2]}"

        games_data = nba.get_games(per_page=100, start_date=date,end_date=date)

        for game in games_data['data']:
            games.append(f"{game['visitor_team']['name']} vs {game['home_team']['name']}")
        
        return games
    
    
    @slash_command(name="game", description="Lists stats for an NBA game")
    async def game(self, ctx, date: Option(str, "Date (YYYY-MM-DD)", required=False), game: Option(str, "Game", autocomplete=get_games, required=False)):     
        if game == None:
            await ctx.respond("Please pick a valid NBA game!", ephemeral=True)
            return
        
        if date == None:
            t = time.localtime()
            date = f"{t[0]}-{t[1]}-{t[2]}"

        games_data = nba.get_games(per_page=100, start_date=date,end_date=date)
        
        for game_data in games_data['data']:
            if game_data["visitor_team"]["name"].lower() != game.split(" vs ")[0].lower():
                continue

            if game_data["home_team"]["name"].lower() != game.split(" vs ")[1].lower():
                continue

            selected_game_data = game_data
        
        if selected_game_data == None:
            await ctx.respond("Please pick a valid NBA game!", ephemeral=True)
            return
        
        embed = discord.Embed(title=f"{selected_game_data['visitor_team']['full_name']} vs {selected_game_data['home_team']['full_name']}")
        
        game_stats = nba.get_stats(game_ids=[selected_game_data["id"]], per_page=100)["data"]

        visitor_players = {}
        home_players = {}
        for player in game_stats:
            if player["min"] == None or len(player["min"].split(":")) != 2 or int(player["min"].split(":")[0]) == 0:
                continue
            if player["team"]["id"] == selected_game_data["visitor_team"]["id"]:
                visitor_players[player["id"]] = player
                
            elif player["team"]["id"] == selected_game_data["home_team"]["id"]:
                home_players[player["id"]] = player
        
        v = sorted(visitor_players, key=lambda x : (int(visitor_players[x]["min"].split(":")[0]) * 60) + int(visitor_players[x]["min"].split(":")[1]))
        v.reverse()

        h = sorted(home_players, key=lambda x : (int(home_players[x]["min"].split(":")[0]) * 60) + int(home_players[x]["min"].split(":")[1]))
        h.reverse()
                
        v_player_description = ""
        v_stats_description = ""
        for player_id in v:
            player = visitor_players[player_id]
            v_player_description += f"{player['player']['first_name']} {player['player']['last_name']}\n"
            v_stats_description += f"{player['min']}, **{player['reb']}** REB, **{player['ast']}** AST, **{player['pts']}** PTS\n"

        h_player_description = ""
        h_stats_description = ""
        for player_id in h:
            player = home_players[player_id]
            h_player_description += f"{player['player']['first_name']} {player['player']['last_name']}\n"
            h_stats_description += f"{player['min']}, **{player['reb']}** REB, **{player['ast']}** AST, **{player['pts']}** PTS\n"


        embed.add_field(name=f"{selected_game_data['visitor_team']['name']} names", value=v_player_description)
        embed.add_field(name=f"{selected_game_data['visitor_team']['name']} stats", value=v_stats_description)
        embed.add_field(name='\u200b', value='\u200b')

        embed.add_field(name=f"{selected_game_data['home_team']['name']} names", value=h_player_description)
        embed.add_field(name=f"{selected_game_data['home_team']['name']} stats", value=h_stats_description)
        embed.add_field(name='\u200b', value='\u200b')

        embed.color = self.bot.embed_color

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.respond(embed=embed)

"""
Registers command when the cog is setup.
"""
def setup(bot):
    bot.add_cog(Game(bot))