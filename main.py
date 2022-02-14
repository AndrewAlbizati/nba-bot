import json
from bot import Bot

if __name__ == "__main__":
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
    
    bot = Bot()
    bot.run(data["discord-bot-token"])