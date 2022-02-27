# NBA Discord Bot
This Discord bot was written in Python 3.10 and uses the [balldontlie API](https://www.balldontlie.io/#introduction).

## How to Run
1. Run `python --version` and ensure it is at least version 3.10
2. In the same folder as all of the files, run `pip install -r requirements.txt`
3. Run `python main.py`
4. Update the newly created `config.json` with the bot's token.
5. Run `python main.py` and wait a few seconds for the bot to collect data.

## Commands
- **/help** Shows all bot commands.
- **/games [date (yyyy-mm-dd)]** Shows all NBA games that are playing on a specified date (defaults to the current day if none provided).
- **/standings** Lists all NBA teams ranked by winning percentage.
- **/team &lt;name>** Returns stats for a particular team in the NBA.
- **/ [date (yyyy-mm-dd)] [game name]** Shows stats for a specified NBA game.


## Notes/Considerations
1. The API cannot accept more than 60 requests per minute.
2. Live game statistics may be off by as much as ten minutes.
3. Only information about current NBA teams is tracked.
4. Pre-season games are not included.


## Dependencies
- Pycord (https://pypi.org/project/py-cord/) `pip install py-cord==2.0.0b4`
- Requests (https://pypi.org/project/requests/) `pip install requests`