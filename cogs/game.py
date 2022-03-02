from discord.commands import slash_command
from discord.ext import commands, pages
from discord import Option
import discord
import time
import nba

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    """
    Returns autocompleted NBA games on a certain date.
    """
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
    
    """
    Returns player stats for an NBA game.
    The date of the game can be configured with the [date] option.
    The user then picks the game in the [game] option from multiple options.
    """
    @slash_command(name="game", description="Lists stats for an NBA game")
    async def game(self, ctx, date: Option(str, "Date (YYYY-MM-DD)", required=False), game: Option(str, "Game", autocomplete=get_games, required=False)):
        if game == None:
            await ctx.respond("Please pick a valid NBA game!", ephemeral=True)
            return
        
        # Defaults to the current date if none is provided
        if date == None:
            t = time.localtime()
            date = f"{t[0]}-{t[1]}-{t[2]}"

        # Searches for the specific game
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
        

        game_stats = nba.get_stats(game_ids=[selected_game_data["id"]], per_page=100)["data"]
        if len(game_stats) == 0:
            await ctx.respond("This game hasn't started yet! Data will appear once this game has started.", ephemeral=True)
            return
        
        # Sort players by their minutes in game
        # Remove players with less than one minute
        visitor_players = {}
        home_players = {}
        for player in game_stats:
            if player["min"] == None or len(player["min"].split(":")) != 2 or int(player["min"].split(":")[0]) == 0:
                continue
            if player["team"]["id"] == selected_game_data["visitor_team"]["id"]:
                visitor_players[player["id"]] = player
                
            elif player["team"]["id"] == selected_game_data["home_team"]["id"]:
                home_players[player["id"]] = player
        
        if len(visitor_players) == 0 and len(home_players) == 0:
            await ctx.respond("This game hasn't started yet! Data will appear once this game has started.", ephemeral=True)
            return
            
        v = sorted(visitor_players, key=lambda x : (int(visitor_players[x]["min"].split(":")[0]) * 60) + int(visitor_players[x]["min"].split(":")[1]))
        v.reverse()

        h = sorted(home_players, key=lambda x : (int(home_players[x]["min"].split(":")[0]) * 60) + int(home_players[x]["min"].split(":")[1]))
        h.reverse()
        
        # Create a list of Discord embeds
        # One embed for each stat
        stats = ["min", "pts", "ast", "blk", "reb", "stl"]
        stats_names = ["Minutes", "Points", "Assists", "Blocks", "Rebounds", "Steals"]
        stats_pages = []
        for i in range(len(stats)):
            embed = discord.Embed(title=f"{selected_game_data['visitor_team']['full_name']} vs {selected_game_data['home_team']['full_name']}")
            embed.color = self.bot.embed_color
            embed.description = f"__{selected_game_data['status']}__\n**{selected_game_data['visitor_team']['abbreviation']}**: {selected_game_data['visitor_team_score']}\n**{selected_game_data['home_team']['abbreviation']}**: {selected_game_data['home_team_score']}"
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar)

            v_stats_description = ""
            for player_id in v:
                player = visitor_players[player_id]
                v_stats_description += f"{player['player']['first_name']} {player['player']['last_name']}: **{player[stats[i]]}**\n"

            h_stats_description = ""
            for player_id in h:
                player = home_players[player_id]
                h_stats_description += f"{player['player']['first_name']} {player['player']['last_name']}: **{player[stats[i]]}**\n"


            embed.add_field(name=f"{selected_game_data['visitor_team']['name']} {stats_names[i]}", value=v_stats_description, inline=True)
            embed.add_field(name=f"{selected_game_data['home_team']['name']} {stats_names[i]}", value=h_stats_description, inline=True)
            
            stats_pages.append([embed])

        
        paginator = pages.Paginator(pages=stats_pages)
        paginator.remove_button("first")
        paginator.remove_button("last")
        await paginator.respond(ctx.interaction, ephemeral=False)

"""
Registers command when the cog is setup.
"""
def setup(bot):
    bot.add_cog(Game(bot))