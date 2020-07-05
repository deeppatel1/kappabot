import discord, json

from python_app.getAnimesAndMangas import all_embeds, load_all_embeds
from python_app.getLeagueMatches import get_future_league_games

client = discord.Client()

with open('configuration.json') as json_file :
    config = json.load(json_file)


@client.event
async def on_message(message):
    if message.content.startswith('!weeb'):
        load_all_embeds()
        for embed in all_embeds:
            await message.channel.send(embed=embed)
        all_embeds.clear()

    if message.content.startswith('!league'):
        future_games, future_embeds = get_future_league_games()
        for x in range(0, len(future_games)):
            if x < 5:
                await message.channel.send(future_games[x])
                await message.channel.send(embed=future_embeds[x])


client.run(config.get("discordclientlogin"))